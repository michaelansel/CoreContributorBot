import os
from lib.constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER
from lib.github import repo
from lib.openai import openai_client
from lib.rag_loop import rag_loop

def process_pull_request_comment(pr, comment):
    title = pr.title
    body = comment.body
    number = pr.number

    response = rag_loop(f"Pull Request: {title}\nComment: {body}")

    code_changes = parse_code_changes(response)

    for code_change in code_changes:
        filename = code_change['filename']
        contents = code_change['contents']

        if not contents:
            repo.delete_file(filename, f"Delete empty file {filename} per PR #{number} comment", branch=pr.head.ref)
            continue

        try:
            existing_file = repo.get_contents(filename, ref=pr.head.sha)
            repo.update_file(filename, f"Update {filename} per PR #{number} comment", contents, existing_file.sha, branch=pr.head.ref)
        except Exception as e:
            repo.create_file(filename, f"Create {filename} per PR #{number} comment", contents, branch=pr.head.ref)

    comment.reply(f"Bot Response: {response}")