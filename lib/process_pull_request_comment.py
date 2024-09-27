from .github import repo
from .openai import openai_client
from .rag_loop import rag_loop
from .parse_code_changes import parse_code_changes

def process_pull_request_comment(pr, comment):
    """
    Process a pull request comment by generating additional code changes and updating the pull request.
    """
    title = pr.title
    body = comment.body

    # Generate additional code changes using the RAG loop
    code_changes = rag_loop(title, body)

    # Parse the generated code changes
    changes_dict = parse_code_changes(code_changes)

    # Update the pull request with the additional code changes
    if changes_dict:
        # Delete empty files instead of updating them
        files_to_delete = [filename for filename, content in changes_dict.items() if not content.strip()]
        for filename in files_to_delete:
            del changes_dict[filename]
            repo.delete_file(filename, f"Delete empty file {filename}", pr)
        
        # Update the pull request with the remaining code changes
        if changes_dict:
            pr.update(changes_dict)
            comment_reply = f"Bot Response: Updated pull request #{pr.number} with additional code changes"
        else:
            comment_reply = "Bot Response: No non-empty files changed"
    else:
        comment_reply = "Bot Response: No additional code changes generated"
    
    # Reply to the pull request comment with the bot's response
    comment.reply(comment_reply)