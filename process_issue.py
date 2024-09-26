from rag_loop import rag_loop
from parse_code_changes import parse_code_changes

def process_issue(issue):
    """
    Process a new issue, generate code changes using a RAG loop, and create a new pull request.
    """
    # Use the RAG loop to generate code changes
    code_changes = rag_loop(f'Title: {issue.title}\nDescription:\n{issue.body}')
    
    if code_changes and code_changes.startswith("CREATE PULL REQUEST"):
        [cpr, title, rest] = code_changes.split("\n\n", 2)

        pr_title = title.split('Title: ')[1]

        # Parse the generated code changes
        parsed_changes = parse_code_changes(rest)
        
        # Extract the pull request title
        # pr_title = parsed_changes.pop('Title', f'Address issue #{issue.number}')

        log(f"Ready to submit code changes for issue #{issue.number}")
        log(f"Pull request title: {pr_title}")
        log(f"Code changes: {parsed_changes}")
        
        # Create a new branch for the code changes
        new_branch = f"issue-{issue.number}"
        repo.create_git_ref(f'refs/heads/{new_branch}', repo.get_git_ref("heads/main").object.sha)
        
        # Update the files with the generated code changes
        for filename, content in parsed_changes.items():
            try:
                file = repo.get_contents(filename, ref=new_branch)
                repo.update_file(
                    path=f'{filename}',
                    message=f'Update {filename} to address issue #{issue.number}',
                    content=content,
                    sha=file.sha,
                    branch=new_branch,
                )
            except:
                repo.create_file(
                    path=f'{filename}',
                    message=f'Update {filename} to address issue #{issue.number}',
                    content=content,
                    branch=new_branch,
                )
        
        # Create a new pull request
        pr = repo.create_pull(
            title=pr_title,
            body=f'Address issue #{issue.number}',
            head=new_branch,
            base=repo.default_branch
        )

        issue.create_comment(f"Handling in PR: {pr.html_url}")
    else:
        log("Unable to parse final response")