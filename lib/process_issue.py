from lib.rag_loop import rag_loop
from lib.constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER

def process_issue(issue):
    title = issue.title
    body = issue.body
    comments = list(issue.get_comments())
    if comments:
        most_recent_comment = comments[-1].body
    else:
        most_recent_comment = ""

    prompt = f"Issue Title: {title}\nIssue Body:\n{body}\nMost Recent Comment:\n{most_recent_comment}\n\nGenerate a code change to resolve the issue. Include the following delimiter to indicate the beginning of each new file's contents: {SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER}"
    
    response = rag_loop(prompt)
    issue.create_comment(f"Bot Response: {response}")