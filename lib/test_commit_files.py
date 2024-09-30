import unittest
from unittest.mock import patch, Mock

from .commit_files import commit_files
from .constants import SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER
from .process_issue import process_issue

class TestCommitFiles(unittest.TestCase):
    @patch('lib.commit_files.repo')
    def test_new_file(self, mock_repo):
        mock_repo.get_contents.side_effect = Mock(side_effect=Exception('Test'))
        mock_repo.create_file.return_value = None
        mock_repo.create_pull.return_value.html_url = "Test URL"

        branch = "issue-1"

        files = {
            "test.txt": "This is a test file."
        }

        commit_files(branch, files, " to address issue #1")
        mock_repo.create_file.assert_called_once_with(
            path="test.txt",
            message='Update test.txt to address issue #1',
            content=files["test.txt"],
            branch=branch,
        )

if __name__ == '__main__':
    unittest.main()
