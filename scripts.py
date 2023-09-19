# Imports
import os
import shutil
import json

import openai

from pydub import AudioSegment
from pydub.utils import make_chunks

from prompts import prompts

from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

MAX_WHISPER_AUDIO_SIZE = 26262828
MAX_CONTEXT_4K = 4097
MAX_CONTEXT_16K = 4097 * 4


### TRANSCRIPTION

# Transcribe the audio file
def transcribe(TASK, AUDIO_FILE_PATH):
    with open(AUDIO_FILE_PATH, "rb") as audio_file:

        file_size = os.stat(AUDIO_FILE_PATH).st_size
        if file_size > MAX_WHISPER_AUDIO_SIZE - 8:
            print(f"Whisper file size limit exceeded. \n    > File size: {file_size}")
            n_chunks = create_chunks(AUDIO_FILE_PATH=AUDIO_FILE_PATH)
            transcript = ""
            for i in range(n_chunks):
                with open('./temp_audio/chunk_{:03d}.mp3'.format(i+1), "rb") as audio_chunk:
                    transcript += whisper_call(TASK, audio_file=audio_chunk)
            try:
                shutil.rmtree('./temp_audio/')
            except:
                print("temp_audio could not be deleted")
        else:
            transcript = whisper_call(TASK, audio_file)
    return transcript

# Deal with audio files that are above Whispers maximum
def create_chunks(AUDIO_FILE_PATH):
    # creates output folder
    try:
        os.makedirs('./temp_audio') 
    except FileExistsError:
        pass

    # set constants
    chunk_length_ms = 15 * 60 * 1000
    audio_file = AudioSegment.from_mp3(AUDIO_FILE_PATH)
    chunks = make_chunks(audio_file, chunk_length_ms)

    # set export paramaters
    for i, chunk in enumerate(chunks, start = 1):
        chunk_name = './temp_audio/chunk_{:03d}.mp3'.format(i)
        print('exporting', os.path.basename(chunk_name))
        chunk.export(chunk_name, format='mp3')
    return len(chunks)

# Make the Whisper call
def whisper_call(TASK, audio_file):
    prompt = prompts[TASK]['whisper_prompt']
    transcript = openai.Audio.transcribe(api_key=OPENAI_API_KEY,
                                        model="whisper-1",
                                        prompt=prompt,
                                        file=audio_file,
                                        response_format="text",
                                        language="en"
                                        )
    return transcript



### TEXT PROCESSING

def process_transcript(TASK, transcript):

    token_estimate = len(transcript) / 4 # average token length
    PROMPT = prompts[TASK]['gpt_prompt']

    if MAX_CONTEXT_4K > token_estimate:
        MODEL = "gpt-3.5-turbo"
        text_response = openai.ChatCompletion.create(api_key=OPENAI_API_KEY, model=MODEL, messages=[
                                                {"role": "system", "content": PROMPT},
                                                {"role": "user", "content": transcript}
                                        ])
        
    elif MAX_CONTEXT_16K > token_estimate > MAX_CONTEXT_4K - 100:
        MODEL = "gpt-3.5-turbo-16k"
        text_response = openai.ChatCompletion.create(api_key=OPENAI_API_KEY, model=MODEL, messages=[
                                                    {"role": "system", "content": PROMPT},
                                                    {"role": "user", "content": transcript}
                                            ])
        
    elif token_estimate > MAX_CONTEXT_16K - 100: # for safety
        # cut transcript
        # run multiple transcripts
        print("NOT IMPLEMENTED YET. CONTEXT WINDOW TOO LONG FOR gpt3.5-16k.")
        pass

    else:
        print("DEBUG: unexpected error. Token_estimate is not captured.")

    return text_response



### NOTION

def list_to_string(l):
    s = ""
    for e in l:
        s += "- " + e + "\n"
    return s

def check_response(text_response):
    content_notion = text_response["choices"][0]["message"]["content"]

    # make sure ass_response is dict
    if type(content_notion) == dict:
        return content_notion
    if type(content_notion) == str:
        try:
            content_notion = json.loads(content_notion)
        except:
            print("ERROR: GPT response is not a dictionary")
            return
    
    # make sure all values are strings
    for k in content_notion:
        if type(content_notion[k]) == str:
            continue
        if type(content_notion[k]) == list:
            content_notion[k] = list_to_string(content_notion[k])
            continue
        else:
            print("ERROR: datatype within list:", type(content_notion[k]))
            return

    return content_notion

def prepare_yield_NOTION(TASK, NOTION_DATABASE_ID, MAX_BLOCK_SIZE,
                         content_notion, transcript):
    # Create Notion API template
    data_database = {
    "parent":   {
        "type": "database_id",
        "database_id": NOTION_DATABASE_ID
                },
    "icon": {"emoji": "🎙️"},
    "properties":   {
        "Name":         {
            "title": [{"text": {"content": content_notion['title']}}] # str(list(content_notion.keys())[0])
                        },
        "Thought":      {
            "select": {"name": TASK}
                        }
        },
    "children": []

                }
    
    # Add TASK content
    for key in content_notion:
        data_database["children"].append({
            "object": "block",
            "heading_2": {"rich_text": [{"text": {"content": key}}]}
        })
        if len(content_notion[key]) > 2000:
            content_chunks = [content_notion[key][i:i+MAX_BLOCK_SIZE] for i in range(0, len(content_notion[key]), MAX_BLOCK_SIZE)]
            for chunk in content_chunks:
                data_database["children"].append({
                    "object": "block",
                    "paragraph": {"rich_text": [{"text": {"content": chunk}}], "color": "default"}
                })
        else:
            data_database["children"].append({
                "object": "block",
                "paragraph": {"rich_text": [{"text": {"content": content_notion[key]}}], "color": "default"}
            })

    # Add transcript
    data_database["children"].append({
            "object": "block",
            "heading_2": {"rich_text": [{"text": {"content": "Transcript"}}]}
        })
    transcript_chunks = [transcript[i:i+MAX_BLOCK_SIZE] for i in range(0, len(transcript), MAX_BLOCK_SIZE)]
    for chunk in transcript_chunks:
            data_database["children"].append({
                "object": "block",
                "paragraph": {"rich_text": [{"text": {"content": chunk}}], "color": "default"}
            })

    return data_database