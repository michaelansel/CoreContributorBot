from parse_code_changes import parse_code_changes
from constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER
import unittest

# Unit tests
class TestParseCodeChanges(unittest.TestCase):    
    def test_single_file_changed(self):
        # Test the parse_code_changes function with a sample output
        code_changes = SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER+""": utils.py
# END FILE CONTENTS
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)
END FILE CONTENTS: utils.py"""
        
        parsed_changes = parse_code_changes(code_changes)
        
        # Assert that the parsed changes contain the expected filename and content
        self.assertIn("utils.py", parsed_changes)
        self.assertEqual(parsed_changes["utils.py"], """# END FILE CONTENTS
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)""")