from .constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER
from .log import log

def parse_code_changes(code_changes):
    """
    Parse the generated code changes into a dictionary of filenames and their updated contents.
    """
    changes_dict = {}
    
    # Split the code changes into separate file updates
    file_updates = code_changes.split(SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER)
    
    for update in file_updates[1:]:
        # Extract the filename and updated content
        if "END FILE CONTENTS" in update:
            filename, content = update.split("\n", 1)
            content = content.rsplit("END FILE CONTENTS", 1)[0].strip()
            
            # Add the filename and content to the changes dictionary
            changes_dict[filename.strip()] = content
        else:
            log("Ignoring change for some reason")
            log(update)
    
    return changes_dict