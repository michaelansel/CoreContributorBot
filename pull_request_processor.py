from rag import rag_loop, parse_code_changes

def process_pull_request_comment(pr, comment, repo):
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