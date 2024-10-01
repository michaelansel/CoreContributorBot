# Helper functions for processing pull requests
from .github import repo

def extract_issue_from_pull_request(pr_body):
    """
    Extract the original issue title and description from the pull request body.
    """
    if pr_body.startswith("Address issue #"):
        number = pr_body.split("Address issue #", 1)[1]
        issue = repo.get_issue(number=int(number))
        return issue.title, issue.body
    
    raise Exception("can't find the associated issue")

def get_proposed_changes(pr):
    """
    Get the proposed code changes from the pull request.
    """
    proposed_changes = {}
    for file in pr.get_files():
        proposed_changes[file.filename] = file.patch
    return proposed_changes