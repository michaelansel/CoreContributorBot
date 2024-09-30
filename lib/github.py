# Initialize GitHub API client and define the repository to monitor
from github import Github
import os

gh_token = os.environ['GITHUB_TOKEN']
gh = Github(gh_token)

repo_name = os.environ['GH_REPO']
repo = gh.get_repo(repo_name)