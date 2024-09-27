import unittest
from unittest.mock import patch
from .rag_loop import rag_loop
from .constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER

class TestRagLoop(unittest.TestCase):
    @patch('lib.openai.call_the_llm')
    def test_rag_loop(self, mock_call_the_llm):
        mock_call_the_llm.return_value = "def hello_world():\n    print('Hello, World!')\n\nhello_world()"

        issue_body = "Please create a function that prints 'Hello, World!'."
        file_contents = ""
        
        response, new_file_contents = rag_loop(issue_body, file_contents)

        self.assertIn("```python", response)
        self.assertIn("def hello_world():", response)
        self.assertIn("print('Hello, World!')", response)
        self.assertIn("hello_world()", response)
        self.assertIn("```", response)

        self.assertEqual(new_file_contents, "def hello_world():\n    print('Hello, World!')\n\nhello_world()\n")

if __name__ == '__main__':
    unittest.main()
