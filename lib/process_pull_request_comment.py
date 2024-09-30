from lib.constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER, SPECIAL_END_FILE_CONTENTS_DELIMETER
from lib.github import repo
from lib.openai import openai_client
from lib.rag_loop import rag_loop
from lib.parse_code_changes import parse_code_changes

def process_pull_request_comment(pr, comment):
    title = pr.title
    body = pr.body
    comment_body = comment.body

    prompt = f"Pull Request Title: {title}\n\nPull Request Body:\n{body}\n\nComment Body:\n{comment_body}\n\n{SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER}\n"
    response, _ = rag_loop(openai_client, prompt, repo.git_repo)

    code_changes = parse_code_changes(response)
    if code_changes:
        repo.update_pull_request(pr, code_changes, response)
        comment.create_comment("Bot Response: Pull request updated")
    else:
        comment.create_comment("Bot Response: No changes suggested")