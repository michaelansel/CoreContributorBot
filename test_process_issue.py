import unittest
from unittest.mock import patch, MagicMock
from lib.process_issue import process_issue

class TestProcessIssue(unittest.TestCase):
    @patch('lib.rag_loop.rag_loop')
    def test_process_issue(self, mock_rag_loop):
        mock_rag_loop.return_value = "Fake code change"
        
        issue = MagicMock()
        issue.title = "Fake issue title"
        issue.body = "Fake issue body"
        issue.get_comments.return_value = [MagicMock(body="Fake comment 1"), MagicMock(body="Fake comment 2")]
        
        process_issue(issue)
        
        prompt = f"Issue Title: Fake issue title\nIssue Body:\nFake issue body\nMost Recent Comment:\nFake comment 2\n\nGenerate a code change to resolve the issue. Include the following delimiter to indicate the beginning of each new file's contents: {SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER}"
        mock_rag_loop.assert_called_once_with(prompt)
        issue.create_comment.assert_called_once_with("Bot Response: Fake code change")

if __name__ == '__main__':
    unittest.main()