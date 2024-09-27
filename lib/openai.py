import os
from openai import OpenAI
from .log import log
import sys

# Initialize OpenAI API client
openai_api_key = os.environ['OPENAI_API_KEY']
openai_api_base = "https://api.lambdalabs.com/v1"

openai_client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

def call_the_llm(prompt):
    print('no!')
    sys.exit(1)
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
        stream=True # Use streaming for easier monitoring and to avoid API timeouts
    )

    log("Response")

    # create variable to collect the stream of messages
    collected_messages = []
    # iterate through the stream of events
    for chunk in response:
        chunk_message = chunk.choices[0].delta.content  # extract the message
        collected_messages.append(chunk_message)  # save the message
        if chunk_message is not None:
            sys.stdout.write(chunk_message) # display the message
    sys.stdout.write("\n") # add a final newline

    # clean None in collected_messages
    collected_messages = [m for m in collected_messages if m is not None]
    output = ''.join(collected_messages)

    # output = response.choices[0].message.content.strip()
    log("Full response")
    log(output)

    return output