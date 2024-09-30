import unittest
from lib.parse_code_changes import parse_code_changes
from lib.constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER

class TestParseCodeChanges(unittest.TestCase):
    def test_empty_file(self):
        code_changes = f"""\
{SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER}
: empty.txt
END FILE CONTENTS: empty.txt
"""
        parsed_changes = parse_code_changes(code_changes)
        
        self.assertIn("empty.txt", parsed_changes)
        self.assertEqual(parsed_changes["empty.txt"], "")

if __name__ == "__main__":
    unittest.main()