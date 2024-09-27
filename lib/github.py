from github import Github

def repo():
    token = os.environ.get('GITHUB_TOKEN')
    repo_name = os.environ.get('GH_REPO')
    g = Github(token)
    return g.get_repo(repo_name)