import os
import unittest
from unittest.mock import patch
import sys
from lib.parse_code_changes import parse_code_changes
from lib.constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER
from lib.log import log
from lib.github import repo
from lib.openai import openai_client
from lib.rag_loop import rag_loop
from lib.process_issue import process_issue

def process_pull_request_comment(pr, comment):
    """
    Process a pull request comment and generate code changes if necessary.
    """
    # Extract the original issue title and description from the pull request body
    issue_title, issue_description = extract_issue_from_pull_request(pr.body)

    # Get the proposed code changes from the pull request
    proposed_changes = get_proposed_changes(pr)

    extra_context = ""
    
    # Add context for the original issue title and description
    extra_context += f"Issue Title: {issue_title}\nIssue Description:\n{issue_description}\n\n"

    # Add context for the proposed code changes
    extra_context += "Proposed Changes:\n"
    for filename, patch in proposed_changes.items():
        extra_context += f"BEGIN FILE {filename}\n{patch}\nEND FILE {filename}\n"
    extra_context += '\n'

    # Use the RAG loop to generate code changes
    code_changes = rag_loop(comment.body, extra_context)
    
    if code_changes:
        # Update the pull request with the generated code changes
        
        # Get the latest commit of the pull request
        latest_commit = pr.get_commits().reversed[0]
        
        # Update the files with the generated code changes
        pr_branch = pr.head.ref
        for filename, content in parse_code_changes(code_changes).items():
            try:
                file = repo.get_contents(filename, ref=pr_branch)
                repo.update_file(
                    path=f'{filename}',
                    message=f'Update {filename} based on feedback',
                    content=content,
                    sha=file.sha,
                    branch=pr_branch,
                )
            except:
                repo.create_file(
                    path=f'{filename}',
                    message=f'Update {filename} based on feedback',
                    content=content,
                    branch=pr_branch,
                )

        pr.create_issue_comment("Bot Response: Updated based on feedback")

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

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Run the unit tests
        unittest.main(argv=[sys.argv[0]], module=test_bot)
    else:
        # Run the bot
        log("Running")
        for issue in repo.get_issues():
            if issue.pull_request:
                log("Ignoring pull request presenting as an issue")
                continue
            if issue.state == 'open':
                if issue.comments == 0:
                    log("Handling an issue")
                    process_issue(issue)
                else:
                    comments = list(issue.get_comments())
                    if comments:
                        most_recent_comment = sorted(comments, key=lambda comment: comment.created_at)[-1]
                        if not most_recent_comment.body.startswith("Bot Response: "):
                            log("Handling an issue")
                            process_issue(issue)

        for pr in repo.get_pulls():
            log(f"PR: {pr.title} ({pr.state}): {pr.comments}")
            if pr.state == 'open' and pr.comments > 0:
                comments = list(pr.get_issue_comments())
                if comments:
                    most_recent_comment = sorted(comments, key=lambda comment: comment.created_at)[-1]
                    log(f'Most recent comment: {most_recent_comment}')
                    if not most_recent_comment.body.startswith("Bot Response: "):
                        log("Handling a pull request")
                        process_pull_request_comment(pr, most_recent_comment)