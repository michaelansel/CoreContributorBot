import os
from lib.constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER

def parse_code_changes(text):
    files = {}
    current_file = None
    current_contents = []

    for line in text.split('\n'):
        if line.startswith(SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER):
            if current_file:
                files[current_file] = '\n'.join(current_contents)
                current_contents = []
            current_file = line[len(SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER):]
        else:
            current_contents.append(line)

    if current_file:
        files[current_file] = '\n'.join(current_contents)

    # Delete files with empty contents
    for file, contents in list(files.items()):
        if not contents.strip():
            del files[file]
            if os.path.exists(file):
                os.remove(file)

    return files