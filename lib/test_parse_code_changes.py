import unittest
from lib.parse_code_changes import parse_code_changes
from lib.constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER

class TestParseCodeChanges(unittest.TestCase):
    def test_single_file_changed(self):
        code_changes = f"""\
{SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER}
: utils.py
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)
END FILE CONTENTS: utils.py
"""
        parsed_changes = parse_code_changes(code_changes)
        self.assertIn("utils.py", parsed_changes)
        self.assertEqual(parsed_changes["utils.py"], "def factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n - 1)\n")

if __name__ == "__main__":
    unittest.main()