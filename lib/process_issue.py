import os
from lib.constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER
from lib.github import repo
from lib.openai import openai_client
from lib.rag_loop import rag_loop

def process_issue(issue):
    # Get the issue title and body
    title = issue.title
    body = issue.body

    # Get the most recent comment on the issue, if any
    comments = list(issue.get_comments())
    if comments:
        most_recent_comment = sorted(comments, key=lambda comment: comment.created_at)[-1]
        most_recent_comment_body = most_recent_comment.body
    else:
        most_recent_comment_body = ""

    # Combine the issue title, body, and most recent comment into a single prompt
    prompt = f"Issue: {title}\n\nDescription:\n{body}\n\nMost Recent Comment:\n{most_recent_comment_body}\n\nSuggested Code Change:"

    # Run the RAG loop to generate the code change
    response = rag_loop(openai_client, prompt)

    # Parse the generated code change
    changed_files = parse_code_changes(response)

    # Create a new pull request with the changed files
    pr = repo.create_pull(title=f"Bot: {title}", body=f"Bot-generated pull request for {issue.html_url}", head="master", base="master")
    for file_path, file_contents in changed_files.items():
        repo.create_file(file_path, f"Bot-generated change for {issue.html_url}", file_contents, branch=pr.head.ref)

    # Post a comment on the issue with a link to the pull request
    issue.create_comment(f"Bot Response: I have created a pull request to address this issue: {pr.html_url}")