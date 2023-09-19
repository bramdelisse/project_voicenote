from flask import Flask, render_template, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

import openai
import os
import requests

from scripts import transcribe, process_transcript, check_response, prepare_yield_NOTION
from prompts import prompts

from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
# PASSWORD = os.environ["PASSWORD"]

# declaring static variables
MAX_WHISPER_AUDIO_SIZE = 26262828
MAX_CONTEXT_4K = 4097
MAX_CONTEXT_16K = 4097 * 4
MAX_BLOCK_SIZE = 2000
THOUGHT = 'daily_reflection' # <- TODO as dropdown

UPLOAD_FOLDER = '/temp/'
# ALLOWED_EXTENSIONS = {'mp3'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1000 * 1000
auth = HTTPBasicAuth()

users = {
    "bram": generate_password_hash('pwampwam')
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

        # save temporary file
        file = request.files['file']
        file.save(file.filename)
        
        # TRANSCRIPTION
        print("Transcription started.")
        with open(file.filename, "rb") as audio_file:
            transcript = transcribe(THOUGHT, audio_file) # also deals with long audio files
        print("Transcription succes!")

        # remove temporary file
        os.remove(file.filename)

        ### TRANSCRIPT PROCESSING ###
        print("Text processing started.")
        text_response = process_transcript(THOUGHT, transcript)
        print("Text processing succes!")


        ########## NOTION ###########
        # PREPARE RESPONSE FOR NOTION
        content_notion = check_response(text_response)

        # NOTION UPLOAD
        url = "https://api.notion.com/v1/pages/"

        headers =   {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
                    }

        data_database = prepare_yield_NOTION(THOUGHT, NOTION_DATABASE_ID, MAX_BLOCK_SIZE,
                                            content_notion, transcript)

        response_get = requests.post(url, headers=headers, json=data_database)
        print("Processed text uploading succesful!")

        return render_template("summarization.html", title_notion='todo', summary_notion='todo', topics_notion='todo', critical_questions_notion='todo')


if __name__ == '__main__':  
    app.run(debug=True,
            host="192.168.2.15",
            port=42069)