import unittest
from unittest.mock import patch, Mock
from .constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER
from .process_issue import process_issue

class TestProcessIssue(unittest.TestCase):
    @patch('lib.process_issue.repo')
    @patch('github.Issue.Issue')
    @patch('lib.process_issue.rag_loop')
    def test_process_issue(self, mock_rag_loop, Issue, mock_repo):
        mock_rag_loop.return_value = "\n\n".join([
            "CREATE PULL REQUEST",
            "Title: Resolving Test issue",
            "\n".join([
                SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER + ": test.txt",
                "This is a test file.",
                "END FILE CONTENTS: test.txt",
            ]),
        ])

        issue = Issue()
        issue.title = 'Test Issue'
        issue.body = 'This is a test issue'
        issue.number = 1
        issue.create_comment.return_value = True

        mock_repo.get_contents.side_effect = Mock(side_effect=Exception('Test'))
        mock_repo.create_file.return_value = None
        mock_repo.create_pull.return_value.html_url = "Test URL"

        process_issue(issue)
        mock_repo.create_file.assert_called_once_with(
            path="test.txt",
            message='Update test.txt to address issue #1',
            content="This is a test file.",
            branch='issue-1',
        )
        mock_rag_loop.assert_called_once()
        mock_repo.create_pull.assert_called_once_with(
            title='Resolving Test issue',
            body='Address issue #1',
            head='issue-1',
            base=mock_repo.default_branch,
        )

if __name__ == '__main__':
    unittest.main()
