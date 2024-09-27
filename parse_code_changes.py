from constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER

def parse_code_changes(code_changes):
    """
    Parse the generated code changes into a dictionary of filenames and their updated contents.
    """
    changes_dict = {}
    
    # Split the code changes into separate file updates
    d = SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER+": "
    file_updates = [(d+e).strip() for e in ("\n"+code_changes).split("\n"+d) if e]
    
    for update in file_updates:
        # Extract the filename and updated content
        if update.startswith(SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER+': ') and "END FILE CONTENTS" in update:
            filename_start = update.index(SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER+': ') + len(SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER+': ')
            filename_end = update.index('\n', filename_start)
            filename = update[filename_start:filename_end].strip()
            
            content_start = filename_end + 1
            content_end = update.rfind('END FILE CONTENTS: '+filename)
            if(content_end < 0):
                log("Unable to locate end delimiter. Failing all parsing.")
                log(update)
                return {}
            content = update[content_start:content_end].strip()
            
            # Add the filename and content to the changes dictionary
            changes_dict[filename] = content
        else:
            log("Ignoring change for some reason")
            log(update)

    return changes_dict