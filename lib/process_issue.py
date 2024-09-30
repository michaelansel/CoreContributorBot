# Process a new issue, generate code changes using a RAG loop, and create a new pull request
from .rag_loop import rag_loop
from .github import repo
from .parse_code_changes import parse_code_changes
from .log import log
from .commit_files import commit_files

def process_issue(issue):
    comments = list(issue.get_comments())
    if comments:
        most_recent_comment = sorted(comments, key=lambda comment: comment.created_at)[-1]
        most_recent_comment_body = most_recent_comment.body
    else:
        most_recent_comment_body = ""
    if most_recent_comment_body:
        prompt_for_comment = f"\nAdditional direction from most recent comment: {most_recent_comment_body}"
    else:
        prompt_for_comment = ""

    code_changes = rag_loop(f'Title: {issue.title}\nDescription:\n{issue.body}{prompt_for_comment}', "")
    
    if code_changes and code_changes.startswith("CREATE PULL REQUEST"):
        [cpr, title, rest] = code_changes.split("\n\n", 2)

        pr_title = title.split('Title: ')[1]

        parsed_changes = parse_code_changes(rest)
        
        log(f"Ready to submit code changes for issue #{issue.number}")
        log(f"Pull request title: {pr_title}")
        log(f"Code changes: {parsed_changes}")
        
        new_branch = f"issue-{issue.number}"
        repo.create_git_ref(f'refs/heads/{new_branch}', repo.get_git_ref("heads/main").object.sha)
        
        commit_files(new_branch, parsed_changes, f" to address issue #{issue.number}")
        
        pr = repo.create_pull(
            title=pr_title,
            body=f'Address issue #{issue.number}',
            head=new_branch,
            base=repo.default_branch
        )

        issue.create_comment(f"Bot Response: Handling in PR: {pr.html_url}")
    else:
        log("Unable to parse final response")