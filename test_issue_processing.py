import unittest
from unittest.mock import patch
from lib.process_issue import process_issue
from lib.github import Issue

class TestProcessIssue(unittest.TestCase):
    @patch('lib.openai.openai_client.create_chat_completion')
    def test_process_issue(self, mock_create_chat_completion):
        mock_create_chat_completion.return_value = {
            'choices': [
                {
                    'message': {
                        'content': 'BEGIN FILE test.txt\nThis is a test file.\nEND FILE test.txt'
                    }
                }
            ]
        }

        issue = Issue({
            'title': 'Test Issue',
            'body': 'This is a test issue',
            'number': 1
        })

        with patch('lib.github.repo') as mock_repo:
            process_issue(issue)
            mock_repo.get_issues.assert_called_once()
            mock_create_chat_completion.assert_called_once_with(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": "Title: Test Issue\nDescription: This is a test issue\nExisting files:"
                    }
                ]
            )
            mock_repo.create_pull.assert_called_once_with(
                title='Test Issue',
                body='Resolves #1\n\nThis pull request was automatically generated by the GitHub bot.',
                head='issue-1',
                base='main',
                files={
                    'test.txt': 'This is a test file.'
                }
            )

if __name__ == '__main__':
    unittest.main()