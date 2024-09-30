import unittest
from unittest.mock import patch
from lib.process_issue import process_issue

class TestProcessIssue(unittest.TestCase):
    @patch('lib.github.Issue')
    @patch('lib.github.Repo')
    @patch('lib.openai.OpenAI')
    @patch('lib.rag_loop.rag_loop')
    @patch('lib.github.parse_code_changes')
    def test_process_issue(self, mock_parse_code_changes, mock_rag_loop, mock_openai, mock_repo, mock_issue):
        # Set up the mock objects
        mock_issue.title = 'Test Issue'
        mock_issue.body = 'This is a test issue.'
        mock_issue.html_url = 'https://github.com/username/repo/issues/1'
        mock_issue.get_comments.return_value = []
        mock_repo.create_pull.return_value.html_url = 'https://github.com/username/repo/pull/1'
        mock_rag_loop.return_value = 'Suggested Code Change:\nBEGIN FILE foo.py\nprint("Hello, World!")\nEND FILE'
        mock_parse_code_changes.return_value = {'foo.py': 'print("Hello, World!")'}

        # Call the function under test
        process_issue(mock_issue)

        # Assert that the expected methods were called
        mock_issue.get_comments.assert_called_once()
        mock_rag_loop.assert_called_once_with(mock_openai, 'Issue: Test Issue\n\nDescription:\nThis is a test issue.\n\nMost Recent Comment:\n\n\nSuggested Code Change:')
        mock_parse_code_changes.assert_called_once_with('Suggested Code Change:\nBEGIN FILE foo.py\nprint("Hello, World!")\nEND FILE')
        mock_repo.create_pull.assert_called_once_with(title='Bot: Test Issue', body='Bot-generated pull request for https://github.com/username/repo/issues/1', head='master', base='master')
        mock_repo.create_file.assert_called_once_with('foo.py', 'Bot-generated change for https://github.com/username/repo/issues/1', 'print("Hello, World!")', branch='master')
        mock_issue.create_comment.assert_called_once_with('Bot Response: I have created a pull request to address this issue: https://github.com/username/repo/pull/1')

if __name__ == '__main__':
    unittest.main()