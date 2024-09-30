import unittest
from lib.parse_code_changes import parse_code_changes
from lib.constants import BEGIN_FILE_TAG, END_FILE_TAG, SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER, SPECIAL_END_FILE_CONTENTS_DELIMETER

class TestParseCodeChanges(unittest.TestCase):
    def test_parse_code_changes(self):
        bot_response = f'''\
{BEGIN_FILE_TAG.format("path/to/file1.txt")}
{SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER}
File 1 contents
line 2
{END_FILE_TAG.format("path/to/file1.txt")}
{BEGIN_FILE_TAG.format("path/to/file2.txt")}
{SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER}
File 2 contents
{END_FILE_TAG.format("path/to/file2.txt")}
'''

        expected = {
            "path/to/file1.txt": "File 1 contents\nline 2",
            "path/to/file2.txt": "File 2 contents",
        }
        self.assertEqual(parse_code_changes(bot_response), expected)

    def test_parse_code_changes_no_files(self):
        bot_response = "No files changed"
        self.assertEqual(parse_code_changes(bot_response), {})

if __name__ == '__main__':
    unittest.main()