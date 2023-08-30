# Imports
import openai
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
NOTION_API_KEY = os.environ["NOTION_API_KEY"]
NOTION_DATABASE_ID = os.environ["NOTION_DATABASE_ID"]

# Transcription
def transcribe(audio_file):
    transcript = openai.Audio.transcribe(api_key=OPENAI_API_KEY,
                                        model="whisper-1",
                                        prompt=None,
                                        file=audio_file,
                                        response_format="text",
                                        language="en"
                                        )
    return transcript