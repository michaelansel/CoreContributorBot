from rag_loop import rag_loop
from parse_code_changes import parse_code_changes

def process_pull_request_comment(pr, comment):
    """
    Process a pull request comment and generate code changes if necessary.
    """
    # Use the RAG loop to generate code changes
    code_changes = rag_loop(comment.body)
    
    if code_changes:
        # Update the pull request with the generated code changes
        pr.create_comment(f"Based on the feedback, here are the proposed code changes:")
        
        # Get the latest commit of the pull request
        latest_commit = pr.get_commits().reversed[0]
        
        # Create a new branch for the code changes
        new_branch = f"update-pr-{pr.number}"
        repo.create_git_ref(f'refs/heads/{new_branch}', latest_commit.sha)
        
        # Update the files with the generated code changes
        for filename, content in parse_code_changes(code_changes).items():
            repo.update_file(f'{new_branch}/{filename}', f'Update {filename} based on feedback', content, latest_commit.sha)