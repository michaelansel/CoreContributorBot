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
from lib.process_pull_request_comment import process_pull_request_comment

if __name__ == '__main__':
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
