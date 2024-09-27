import os
from openai import OpenAI

# Initialize OpenAI API client
openai_api_key = os.environ['OPENAI_API_KEY']
openai_api_base = "https://api.lambdalabs.com/v1"

openai_client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)