import unittest
from unittest.mock import MagicMock, patch
from lib.process_issue import process_issue
from lib.github import repo

class TestProcessIssue(unittest.TestCase):
    @patch("lib.process_issue.repo")
    @patch("lib.process_issue.rag_loop")
    def test_process_issue(self, mock_rag_loop, mock_repo):
        issue = MagicMock()
        issue.title = "Test Issue"
        issue.body = "This is a test issue"

        mock_rag_loop.return_value = "CREATE PULL REQUEST\n\nTitle: Address Test Issue\n\nBEGIN FILE CONTENTS: test.txt\nThis is a test file\nEND FILE CONTENTS: test.txt"

        process_issue(issue)

        mock_rag_loop.assert_called_once_with("Test Issue", "This is a test issue")
        mock_repo.create_file.assert_called_once_with(
            path="test.txt",
            message="Update test.txt to address issue #1",
            content="This is a test file",
            branch="issue-1"
        )
        mock_repo.create_pull.assert_called_once_with(
            title="Address Test Issue",
            body="Address issue #1",
            head="issue-1",
            base=mock_repo.default_branch
        )

if __name__ == "__main__":
    unittest.main()