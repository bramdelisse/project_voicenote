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



### TEXT PROCESSING



### NOTION

def create_data_database(NOTION_DATABASE_ID, MAX_BLOCK_SIZE,
                         title_notion, summary_notion, topics_notion, critical_questions_notion,
                         transcript):
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
        },
        {
            "object": "block",
            "heading_2": {"rich_text": [{"text": {"content": "Transcript"}}]}
        }
                ]

                }
    
    transcript_chunks = [transcript[i:i+MAX_BLOCK_SIZE] for i in range(0, len(transcript), MAX_BLOCK_SIZE)]
    for chunk in transcript_chunks:
            data_database["children"].append({
                "object": "block",
                "paragraph": {"rich_text": [{"text": {"content": chunk}}], "color": "default"}
            })

    return data_database