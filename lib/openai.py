# Initialize OpenAI API client and define helper functions
import os
from openai import OpenAI
from .log import log
import sys

openai_api_key = os.environ['OPENAI_API_KEY']
openai_api_base = "https://api.lambdalabs.com/v1"

openai_client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

def call_the_llm(prompt):
    log("Request")
    log(prompt)

    response = openai_client.chat.completions.create(
        model='hermes-3-llama-3.1-405b-fp8-128k',
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=10000,
        stream=True
    )

    log("Response")

    collected_messages = []
    for chunk in response:
        chunk_message = chunk.choices[0].delta.content
        collected_messages.append(chunk_message)
        if chunk_message is not None:
            sys.stdout.write(chunk_message)
    sys.stdout.write("\n")

    collected_messages = [m for m in collected_messages if m is not None]
    output = ''.join(collected_messages)

    log("Full response")
    log(output)

    return output