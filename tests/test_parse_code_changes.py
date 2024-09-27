import unittest
from lib.parse_code_changes import parse_code_changes
from lib.constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER

class TestParseCodeChanges(unittest.TestCase):
    def test_parse_code_changes(self):
        text = f"Random text\n{SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER}file1.txt\nFile 1 contents\n{SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER}file2.txt\nFile 2 contents\n"
        files = parse_code_changes(text)
        self.assertEqual(files, {
            'file1.txt': 'File 1 contents',
            'file2.txt': 'File 2 contents'
        })

    def test_empty_file_contents(self):
        text = f"Random text\n{SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER}file1.txt\nFile 1 contents\n{SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER}file2.txt\n"
        files = parse_code_changes(text)
        self.assertEqual(files, {
            'file1.txt': 'File 1 contents'
        })
        self.assertFalse(os.path.exists('file2.txt'))

if __name__ == '__main__':
    unittest.main()