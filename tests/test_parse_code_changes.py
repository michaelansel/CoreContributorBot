import unittest
from lib.parse_code_changes import parse_code_changes
from lib.constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER

class TestParseCodeChanges(unittest.TestCase):
    def test_parse_code_changes(self):
        code_changes = f"""\
{SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER}
lib/file1.py
def foo():
    pass
{SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER}
lib/file2.py
def bar():
    pass
"""
        expected = {
            "lib/file1.py": "def foo():\n    pass\n",
            "lib/file2.py": "def bar():\n    pass\n"
        }
        self.assertEqual(parse_code_changes(code_changes), expected)

if __name__ == "__main__":
    unittest.main()