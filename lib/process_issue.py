import os
from lib.constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER
from lib.github import repo
from lib.openai import openai_client
from lib.rag_loop import rag_loop

def process_issue(issue):
    title = issue.title
    body = issue.body
    number = issue.number

    response = rag_loop(f"Issue: {title}\n{body}")

    code_changes = parse_code_changes(response)

    for code_change in code_changes:
        filename = code_change['filename']
        contents = code_change['contents']

        if not contents:
            repo.delete_file(filename, f"Delete empty file {filename} per issue #{number}", branch='main')
            continue

        try:
            existing_file = repo.get_contents(filename, ref='main')
            repo.update_file(filename, f"Update {filename} per issue #{number}", contents, existing_file.sha, branch='main')
        except Exception as e:
            repo.create_file(filename, f"Create {filename} per issue #{number}", contents, branch='main')

    issue.create_comment(f"Bot Response: {response}")