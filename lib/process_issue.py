from .rag_loop import rag_loop
from .github import repo
from .openai import openai_client
from .parse_code_changes import parse_code_changes
from .log import log

def process_issue(issue):
    """
    Process a GitHub issue by generating code changes using the RAG loop and creating a pull request.
    """
    title = issue.title
    body = issue.body

    # Generate code changes using the RAG loop
    code_changes = rag_loop(title, body)

    # Parse the generated code changes
    changes_dict = parse_code_changes(code_changes)

    # Create a pull request with the code changes
    if changes_dict:
        # Delete empty files instead of updating them
        files_to_delete = [filename for filename, content in changes_dict.items() if not content.strip()]
        for filename in files_to_delete:
            del changes_dict[filename]
            repo.delete_file(filename, f"Delete empty file {filename}", issue)
        
        # Create a pull request with the remaining code changes
        if changes_dict:
            pr = repo.create_pull(title, changes_dict, issue)
            issue_comment = f"Bot Response: Created pull request #{pr.number} with code changes"
        else:
            issue_comment = "Bot Response: No non-empty files changed"
    else:
        issue_comment = "Bot Response: No code changes generated"
    
    # Add a comment to the issue with the bot's response
    issue.create_comment(issue_comment)