import unittest
from unittest.mock import MagicMock, patch
from lib.process_issue import process_issue

class TestProcessIssue(unittest.TestCase):
    @patch('lib.process_issue.repo')
    @patch('lib.process_issue.openai_client')
    @patch('lib.process_issue.rag_loop')
    def test_process_issue(self, mock_rag_loop, mock_openai_client, mock_repo):
        issue = MagicMock()
        issue.title = 'Test Issue'
        issue.body = 'This is a test issue'
        issue.number = 1

        mock_rag_loop.return_value = [
            {
                'filename': 'test_file.txt',
                'contents': 'This is a test file'
            },
            {
                'filename': 'empty_file.txt',
                'contents': ''
            }
        ]

        process_issue(issue)

        mock_rag_loop.assert_called_once()
        mock_repo.get_contents.assert_any_call('test_file.txt', ref='main')
        mock_repo.update_file.assert_called_once()
        mock_repo.delete_file.assert_called_once()

if __name__ == '__main__':
    unittest.main()