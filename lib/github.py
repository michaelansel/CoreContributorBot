from github import Github
import os

# Initialize GitHub API client
gh_token = os.environ['GITHUB_TOKEN']
gh = Github(gh_token)

# Define the repository to monitor
repo_name = os.environ['GH_REPO']
repo = gh.get_repo(repo_name)