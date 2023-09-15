########## PREAMBLE ###########################################################

# general imports
import openai
import os
import requests

# import scripts
from scripts import transcribe, process_transcript, prepare_data_NOTION, create_data_NOTION
from prompts import prompts

# declaring secrets
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]



########## DECLARING VARIABLES ################################################

AUDIO_FILE_PATH = "./voicenotes/230831-reflection_daily.mp3"
TASK = "daily_reflection"

MAX_WHISPER_AUDIO_SIZE = 26262828
MAX_CONTEXT_4K = 4097
MAX_CONTEXT_16K = 4097 * 4


########## THOUGHT PROCESSING #################################################

####### TRANSCRIPTION #######
print("Transcription started.")
transcript = transcribe(TASK, AUDIO_FILE_PATH) # also deals with long audio files
print("Transcription finished!")


### TRANSCRIPT PROCESSING ###
print("Text processing started.")
text_response = process_transcript(TASK, transcript)
print("Text processing succes!")


########## NOTION ###########
# PREPARE RESPONSE FOR NOTION
content_notion = prepare_data_NOTION(TASK, text_response)

title_notion = content_notion['title_notion']
summary_notion = content_notion['summary_notion']
topics_notion = content_notion['topics_notion']
critical_questions_notion = content_notion['critical_questions_notion']

# NOTION UPLOAD
MAX_BLOCK_SIZE = 2000
url = "https://api.notion.com/v1/pages/"

headers =   {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
            }

data_database = create_data_NOTION(TASK, NOTION_DATABASE_ID, MAX_BLOCK_SIZE, # deals with transcripts longer then Notion max block size
                                     title_notion, summary_notion, topics_notion, critical_questions_notion,
                                     transcript)

response_get = requests.post(url, headers=headers, json=data_database)
print("Processed text uploading succesful!")