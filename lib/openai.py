import os
import openai

def openai_client():
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    return openai