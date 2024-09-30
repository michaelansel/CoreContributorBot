# Process a pull request comment and generate code changes if necessary
from .commit_files import commit_files
from .github import repo
from .pr_helpers import extract_issue_from_pull_request, get_proposed_changes
from .rag_loop import rag_loop
from .parse_code_changes import parse_code_changes

def process_pull_request_comment(pr, comment):
    issue_title, issue_description = extract_issue_from_pull_request(pr.body)

    proposed_changes = get_proposed_changes(pr)

    extra_context = ""
    
    extra_context += f"Issue Title: {issue_title}\nIssue Description:\n{issue_description}\n\n"

    extra_context += "Proposed Changes:\n"
    for filename, patch in proposed_changes.items():
        extra_context += f"BEGIN FILE {filename}\n{patch}\nEND FILE {filename}\n"
    extra_context += '\n'

    code_changes = rag_loop(comment.body, extra_context)
    
    if code_changes:
        pr_branch = pr.head.ref
        changed_files = parse_code_changes(code_changes)
        commit_files(pr_branch, changed_files, " based on feedback")

        pr.create_issue_comment("Bot Response: Updated based on feedback")