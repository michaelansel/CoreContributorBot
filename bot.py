import os
from github import Github
from rag import process_issue, process_pull_request_comment

# Initialize GitHub API client
gh_token = os.environ['GITHUB_TOKEN']
gh = Github(gh_token)

# Define the repository to monitor
repo_name = os.environ['GH_REPO']
repo = gh.get_repo(repo_name)

if __name__ == '__main__':
    for issue in repo.get_issues():
        if issue.pull_request:
            continue
        if issue.state == 'open' and issue.comments == 0:
            process_issue(issue)

    for pr in repo.get_pulls():
        if pr.state == 'open' and pr.comments > 0:
            comments = list(pr.get_issue_comments())
            if comments:
                most_recent_comment = sorted(comments, key=lambda comment: comment.created_at)[-1]
                if not most_recent_comment.body.startswith("Bot Response: "):
                    process_pull_request_comment(pr, most_recent_comment)