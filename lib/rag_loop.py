import os
import openai
from lib.constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER

def rag_loop(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].text.strip()