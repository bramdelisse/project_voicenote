########## PREAMBLE ###########################################################

# general imports
import openai
import os
import requests
import json

# import scripts
from scripts import transcribe, process_transcript, check_response, prepare_yield_NOTION
from prompts import prompts

# declaring secrets
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]



########## DECLARING VARIABLES ################################################

# declaring static variables
MAX_WHISPER_AUDIO_SIZE = 26262828
MAX_CONTEXT_4K = 4097
MAX_CONTEXT_16K = 4097 * 4
MAX_BLOCK_SIZE = 2000

# declaring dynamic variables
AUDIO_FILE_PATH = "./to_process/230901-geluidsopname_gesprek_youri.mp3"
THOUGHT = "nederlands" # "daily_reflection", "blog", "nederlands"


########## THOUGHT PROCESSING #################################################

####### TRANSCRIPTION #######
print("Transcription started.")
transcript = transcribe(THOUGHT, AUDIO_FILE_PATH) # also deals with long audio files
print("Transcription finished!")


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