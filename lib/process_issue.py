import openai
from lib.github import repo
from lib.rag_loop import rag_loop

def process_issue(issue):
    prompt = f"Issue Title: {issue.title}\nIssue Body:\n{issue.body}\n\nRespond to the issue with a comment:"
    response = rag_loop(prompt)
    issue.create_comment(f"Bot Response: {response}")