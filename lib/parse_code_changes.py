import re
from lib.constants import BEGIN_FILE_TAG, END_FILE_TAG, SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER, SPECIAL_END_FILE_CONTENTS_DELIMETER

def parse_code_changes(bot_response):
    file_changes = {}
    current_file_path = None
    current_file_contents = []

    lines = bot_response.split('\n')
    for line in lines:
        if line.startswith(BEGIN_FILE_TAG.format('')):
            current_file_path = re.search(r'PATH="(.+?)"', line).group(1)
        elif line.startswith(SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER):
            current_file_contents = []
        elif line.startswith(END_FILE_TAG.format('')):
            file_changes[current_file_path] = '\n'.join(current_file_contents)
            current_file_path = None
            current_file_contents = []
        elif current_file_path:
            current_file_contents.append(line)

    return file_changes