import os
from github import Github

from issue_processor import process_issue
from pull_request_processor import process_pull_request_comment

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize GitHub API client
gh_token = os.environ['GITHUB_TOKEN']
gh = Github(gh_token)

# Define the repository to monitor
repo_name = os.environ['GH_REPO']
repo = gh.get_repo(repo_name)

if __name__ == '__main__':
    for issue in repo.get_issues():
        if issue.pull_request:
            log("Ignoring pull request presenting as an issue")
            continue
        if issue.state == 'open' and issue.comments == 0:
            log("Handling an issue")
            process_issue(issue, repo)

    for pr in repo.get_pulls():
        log(f"PR: {pr.title} ({pr.state}): {pr.comments}")
        if pr.state == 'open' and pr.comments > 0:
            comments = list(pr.get_issue_comments())
            if comments:
                most_recent_comment = sorted(comments, key=lambda comment: comment.created_at)[-1]
                log(f'Most recent comment: {most_recent_comment}')
                if not most_recent_comment.body.startswith("Bot Response: "):
                    log("Handling a pull request")
                    process_pull_request_comment(pr, most_recent_comment, repo)