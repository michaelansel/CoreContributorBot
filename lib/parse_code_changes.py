from .constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER
from .log import log

def parse_code_changes(code_changes):
    """
    Parse the code changes from the LLM output.
    """
    files = code_changes.split(SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER)
    changes_dict = {}
    for file in files:
        file = file.strip()
        if file:
            filename, content = file.split("\n", 1)
            changes_dict[filename.strip()] = content
    return changes_dict