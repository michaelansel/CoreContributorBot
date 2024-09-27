import unittest
from unittest.mock import patch
from bot import process_issue, rag_loop

class TestIssueProcessing(unittest.TestCase):
    @patch('bot.rag_loop')
    def test_process_issue(self, mock_rag_loop):
        # Mock the RAG loop response
        mock_rag_loop.return_value = "Test code changes"
        
        # Create a mock issue
        mock_issue = unittest.mock.Mock(title="Test issue", body="Test issue description")
        
        # Call the process_issue function
        process_issue(mock_issue)
        
        # Assert that the RAG loop was called with the expected prompt
        mock_rag_loop.assert_called_once_with("Test issue description")
        
        # Assert that the issue was updated with the generated code changes
        mock_issue.create_comment.assert_called_once_with("Bot Response:\n```\nTest code changes\n```")

if __name__ == '__main__':
    unittest.main()