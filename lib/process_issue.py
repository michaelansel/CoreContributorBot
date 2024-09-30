from lib.constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER, SPECIAL_END_FILE_CONTENTS_DELIMETER
from lib.github import repo
from lib.openai import openai_client
from lib.rag_loop import rag_loop
from lib.parse_code_changes import parse_code_changes

def process_issue(issue):
    title = issue.title
    body = issue.body

    prompt = f"Issue Title: {title}\n\nIssue Body:\n{body}\n\n{SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER}\n"
    response, _ = rag_loop(openai_client, prompt, repo.git_repo)

    code_changes = parse_code_changes(response)
    if code_changes:
        pr = repo.create_pull_request(issue, code_changes, response)
        if pr:
            issue.edit(state='closed')
            issue.create_comment(f"Bot Response: Pull request created: {pr.html_url}")
        else:
            issue.create_comment("Bot Response: No changes suggested")
    else:
        issue.create_comment("Bot Response: No changes suggested")