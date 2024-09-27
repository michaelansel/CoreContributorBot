import unittest
from unittest.mock import patch
from .constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER
from .rag_loop import rag_loop

class TestRagLoop(unittest.TestCase):
    @patch('lib.rag_loop.repo')
    @patch('lib.rag_loop.call_the_llm')
    def test_returns_llm_output(self, mock_call_the_llm, mock_repo):
        mock_call_the_llm.return_value = "def hello_world():\n    print('Hello, World!')\n\nhello_world()"

        issue_body = "Please create a function that prints 'Hello, World!'."
        file_contents = ""
        
        response = rag_loop(issue_body, file_contents)

        self.assertIn("def hello_world():\n    print('Hello, World!')\n\nhello_world()", response)

if __name__ == '__main__':
    unittest.main()
