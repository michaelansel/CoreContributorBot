import unittest
from unittest.mock import MagicMock, patch
from lib.process_pull_request_comment import process_pull_request_comment

class TestProcessPullRequestComment(unittest.TestCase):
    @patch('lib.process_pull_request_comment.repo')
    @patch('lib.process_pull_request_comment.openai_client')
    @patch('lib.process_pull_request_comment.rag_loop')
    def test_process_pull_request_comment(self, mock_rag_loop, mock_openai_client, mock_repo):
        pr = MagicMock()
        pr.number = 1
        comment = MagicMock()
        comment.body = 'This is a test comment'

        mock_rag_loop.return_value = [
            {
                'filename': 'test_file.txt',
                'contents': 'This is an updated test file'
            },
            {
                'filename': 'empty_file.txt',
                'contents': ''
            }
        ]

        process_pull_request_comment(pr, comment)

        mock_rag_loop.assert_called_once()
        mock_repo.get_contents.assert_any_call('test_file.txt', ref=pr.head.sha)
        mock_repo.update_file.assert_called_once()
        mock_repo.delete_file.assert_called_once()

if __name__ == '__main__':
    unittest.main()