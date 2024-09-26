from openai import OpenAI

SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER = " ".join(["###","BEGIN","FILE","CONTENTS"])

def rag_loop(prompt, openai_client, repo):
    # ... (rest of the rag_loop function) ...

def parse_code_changes(code_changes):
    # ... (rest of the parse_code_changes function) ...