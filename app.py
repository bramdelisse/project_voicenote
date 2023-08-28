from distutils.log import debug
from fileinput import filename
from flask import Flask, render_template, request, flash, redirect
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

import openai
import os
import requests

from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

UPLOAD_FOLDER = '/temp/'
ALLOWED_EXTENSIONS = {'mp3'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1000 * 1000
auth = HTTPBasicAuth()

users = {
    "bram": generate_password_hash("pwampwam")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username

@app.route('/')
@auth.login_required
def index():
    return render_template("index.html")

@app.route('/upload', methods = ['POST'])
def upload():
    if request.method == 'POST':

        # RECEIVING AUDIO FILE
        # ### testing
        # print("="*20, "Testing starts")
        # blob = request.files['data']
        # print("="*20, "Testing stops")
        # ### testing

        file = request.files['file']
        name = file.filename + ".ogg"
        file.save(name)
        print(file.mimetype)
        
        # TRANSCRIPTION
        print("Transcription started!")
        with open(name, "rb") as voice_note:
            print("File opened?")
            transcript = openai.Audio.transcribe(api_key=OPENAI_API_KEY,
                                        model="whisper-1",
                                        file=voice_note,
                                        response_format="text",
                                        language="en"
                                        )

        print("Transcription succes!")

        # SUMMARIZATION
        summary_prompt      = """\
You are a helpful assistant, specialized in summarizing and understanding the core of a given message. \
For the given piece of text, you are going to perform the following four tasks. \
Firstly, start your response with a consice title describing the text. \
Secondly, summarize in first person the content of this text in one coherent story of about one alinea written. \
Thirdly, list the different topics discussed in this text. Only add a topic when it is discussed for at least a couple of sentences. \
Fourth, imagine being a critical life coach of the person writing this text. What are the three best questions you could ask regarding this text?\
"""
        text_response = openai.ChatCompletion.create(api_key=OPENAI_API_KEY,
                                                    model="gpt-3.5-turbo",
                                                    messages=[
                                                        {"role": "system", "content": summary_prompt},
                                                        {"role": "user", "content": transcript}
                                             ])

        # NOTION
        content_notion = text_response["choices"][0]["message"]["content"].split("\n\n")

        title_notion = "Not found"
        summary_notion = "Not found"
        topics_notion = "Not found"
        critical_questions_notion = "Not found"

        try:
            title_notion = content_notion[0]
        except:
            pass
        try:
            summary_notion = content_notion[1]
        except:
            pass
        try:
            topics_notion = content_notion[2]
        except:
            pass
        try:
            critical_questions_notion = content_notion[3]
        except:
            pass

        url = "https://api.notion.com/v1/pages/"

        headers =   {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
                    }

        data_database = {
        
            "parent":   {
                "type": "database_id",
                "database_id": NOTION_DATABASE_ID
                        },
            "icon": {"emoji": "🎙️"},

            "properties":   {
                "Name":         {
                    "title": [{"text": {"content": title_notion}}]
                                }  
                            },

            "children": [
                {
                    "object": "block",
                    "heading_2": {"rich_text": [{"text": {"content": "Summary"}}]}
                },
                {
                    "object": "block",
                    "paragraph": {"rich_text": [{"text": {"content": summary_notion}}], "color": "default"}
                },
                {
                    "object": "block",
                    "heading_2": {"rich_text": [{"text": {"content": "Topics"}}]}
                },
                {
                    "object": "block",
                    "paragraph": {"rich_text": [{"text": {"content": topics_notion}}], "color": "default"}
                },
                {
                    "object": "block",
                    "heading_2": {"rich_text": [{"text": {"content": "Critical Questions"}}]}
                },
                {
                    "object": "block",
                    "paragraph": {"rich_text": [{"text": {"content": critical_questions_notion}}], "color": "default"}
                }
                        ]

                        }

        response_get = requests.post(url, headers=headers, json=data_database)

        return render_template("summarization.html", title_notion=title_notion, summary_notion=summary_notion, topics_notion=topics_notion, critical_questions_notion=critical_questions_notion)


if __name__ == '__main__':  
    app.run(debug=True)