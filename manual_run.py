########## PREAMBLE ###########################################################

# general imports
import openai
import os
import requests

# import scripts
from scripts import create_chunks, transcribe, whisper_call, create_data_database
from prompts import prompts

# declaring secrets
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]



########## DECLARING VARIABLES ################################################

AUDIO_FILE_PATH = "./voicenotes/230831-reflection_daily.mp3"
PROMPT = prompts['summary_prompt']

MAX_WHISPER_AUDIO_SIZE = 26262828
MAX_CONTEXT_4K = 4097
MAX_CONTEXT_16K = 4097 * 4


########## AUDIO PROCESSING ###################################################

# TRANSCRIPTION
print("Transcription started.")
transcript = transcribe(AUDIO_FILE_PATH) # also deals with long audio files
print("Transcription finished!")

# TRANSCRIPT PROCESSING
print("Text processing started.")
token_estimate = len(transcript) / 4 # average token length
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
    pass
else:
    print("DEBUG: unexpected error. Token_estimate is not captured.")

print("Text processing succes!")

# PREPARE RESPONSE FOR NOTION
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


# NOTION UPLOAD
MAX_BLOCK_SIZE = 2000
url = "https://api.notion.com/v1/pages/"

headers =   {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
            }

data_database = create_data_database(NOTION_DATABASE_ID, MAX_BLOCK_SIZE,
                                     title_notion, summary_notion, topics_notion, critical_questions_notion,
                                     transcript)

response_get = requests.post(url, headers=headers, json=data_database)
print("Processed text uploading succesful!")