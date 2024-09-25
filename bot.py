import os
from openai import OpenAI
from github import Github
import unittest
from unittest.mock import patch
import sys

# Initialize GitHub API client
gh_token = os.environ['GITHUB_TOKEN']
gh = Github(gh_token)

# Initialize OpenAI API client
openai_api_key = os.environ['OPENAI_API_KEY']
openai_api_base = "https://api.lambdalabs.com/v1"

openai_client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

# Define the repository to monitor
repo_name = os.environ['GH_REPO']
repo = gh.get_repo(repo_name)

def process_issue(issue):
    """
    Process a new issue, generate code changes using a RAG loop, and create a new pull request.
    """
    # Use the RAG loop to generate code changes
    code_changes = rag_loop(issue.body)
    
    if code_changes:
        # Parse the generated code changes
        parsed_changes = parse_code_changes(code_changes)
        
        # Extract the pull request title
        pr_title = parsed_changes.pop('Title', f'Address issue #{issue.number}')
        
        # Create a new branch for the code changes
        new_branch = f"issue-{issue.number}"
        repo.create_git_ref(f'refs/heads/{new_branch}', repo.get_commits().reversed[0].sha)
        
        # Update the files with the generated code changes
        for filename, content in parsed_changes.items():
            repo.update_file(f'{new_branch}/{filename}', f'Update {filename} to address issue #{issue.number}', content, repo.get_commits().reversed[0].sha)
        
        # Create a new pull request
        repo.create_pull(title=pr_title, body=f'Address issue #{issue.number}', head=new_branch, base=repo.default_branch)

def process_pull_request_comment(pr, comment):
    """
    Process a pull request comment and generate code changes if necessary.
    """
    # Use the RAG loop to generate code changes
    code_changes = rag_loop(comment.body)
    
    if code_changes:
        # Update the pull request with the generated code changes
        pr.create_comment(f"Based on the feedback, here are the proposed code changes:")
        
        # Get the latest commit of the pull request
        latest_commit = pr.get_commits().reversed[0]
        
        # Create a new branch for the code changes
        new_branch = f"update-pr-{pr.number}"
        repo.create_git_ref(f'refs/heads/{new_branch}', latest_commit.sha)
        
        # Update the files with the generated code changes
        for filename, content in parse_code_changes(code_changes).items():
            repo.update_file(f'{new_branch}/{filename}', f'Update {filename} based on feedback', content, latest_commit.sha)

def rag_loop(prompt):
    """
    Generate code changes using a RAG loop.
    """
    context = ''

    while True:
        # Use OpenAI to analyze the prompt and generate code changes or request additional context
        response = client.chat.completions.create(
            engine='hermes-3-llama-3.1-405b-fp8-128k',
            prompt=f'Context:\n{context}\n\nAnalyze the prompt below and generate code changes. If additional context is needed, request it by specifying the file path:\n{prompt}\n\nFormat the response as follows:\n\nTitle: [Title of the pull request]\n\nFile: [Path to the file]\n[Updated content of the file]\n\nFile: [Path to another file]\n[Updated content of another file]',
            temperature=0.5,
            max_tokens=1000
        )

        output = response.choices[0].text.strip()

        if output.startswith('Request context: '):
            # Retrieve the requested context (e.g., existing code files)
            file_path = output.replace('Request context: ', '').strip()
            context += f'File: {file_path}\n{repo.get_contents(file_path).decoded_content.decode()}\n\n'
        else:
            return output

def parse_code_changes(code_changes):
    """
    Parse the generated code changes into a dictionary of filenames and their updated contents.
    """
    changes_dict = {}
    
    # Split the code_changes into separate file updates
    file_updates = code_changes.split('\n\n')
    
    for update in file_updates:
        # Extract the filename and updated content
        filename, content = update.split('\n', 1)
        
        # Remove the "File: " prefix from the filename
        filename = filename.replace('File: ', '').strip()
        
        # Add the filename and content to the changes dictionary
        changes_dict[filename] = content.strip()
    
    return changes_dict

# Unit tests
class TestGitHubBot(unittest.TestCase):
    @patch.object(OpenAI, 'chat')
    def test_rag_loop(self, mock_openai):
        # Test the RAG loop with a sample prompt and mocked OpenAI response
        prompt = "Add a new function to the utils.py file that calculates the factorial of a given number"
        mock_openai.completions.create.return_value = unittest.mock.Mock(choices=[unittest.mock.Mock(text="""Title: Add factorial function
        
        File: utils.py
        def factorial(n):
            if n == 0:
                return 1
            else:
                return n * factorial(n - 1)
        """)])
        
        code_changes = rag_loop(prompt)
        
        # Assert that the code changes contain the expected function
        self.assertIn("def factorial(n):", code_changes)
    
    def test_parse_code_changes(self):
        # Test the parse_code_changes function with a sample output
        code_changes = """Title: Add factorial function
        
        File: utils.py
        def factorial(n):
            if n == 0:
                return 1
            else:
                return n * factorial(n - 1)
        """
        
        parsed_changes = parse_code_changes(code_changes)
        
        # Assert that the parsed changes contain the expected filename and content
        self.assertIn("utils.py", parsed_changes)
        self.assertEqual(parsed_changes["utils.py"], """def factorial(n):
            if n == 0:
                return 1
            else:
                return n * factorial(n - 1)""")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Run the unit tests
        unittest.main()
    else:
        # Run the bot
        for issue in repo.get_issues():
            if issue.state == 'open' and issue.comments == 0:
                process_issue(issue)

        for pr in repo.get_pulls():
            for comment in pr.get_comments():
                if comment.user != gh.get_user():
                    process_pull_request_comment(pr, comment)