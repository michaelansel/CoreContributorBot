import os
import logging
from github import Github
import sys

from rag import rag_loop, parse_code_changes
from handlers import process_issue, process_pull_request_comment

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Log a message
def log(message):
    logging.info(message)

# Initialize GitHub API client
gh_token = os.environ['GITHUB_TOKEN']
gh = Github(gh_token)

# Define the repository to monitor
repo_name = os.environ['GH_REPO']
repo = gh.get_repo(repo_name)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Run the unit tests
        from tests import run_tests
        run_tests()
    else:
        # Run the bot
        log("Running")
        for issue in repo.get_issues():
            log("Handling an issue")
            if issue.state == 'open' and issue.comments == 0:
                process_issue(issue, repo, rag_loop, parse_code_changes)

        for pr in repo.get_pulls():
            for comment in pr.get_comments():
                if comment.user != gh.get_user():
                    process_pull_request_comment(pr, comment, repo, rag_loop, parse_code_changes)