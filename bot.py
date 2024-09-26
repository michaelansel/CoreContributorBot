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

# Special keyword that can never appear in the code or it breaks the self-management behavior
# Reason: we split files in the LLM output on this keyword, so it should only exist in the LLM "meta" output
BEGIN_FILE_CONTENTS = "_".join(["BEGIN","FILE","CONTENTS"])

def process_issue(issue):
    """
    Process a new issue, generate code changes using a RAG loop, and create a new pull request.
    """
    # Use the RAG loop to generate code changes
    code_changes = rag_loop(f'Title: {issue.title}\nDescription:\n{issue.body}')
    
    if code_changes and code_changes.startswith("CREATE PULL REQUEST"):
        [cpr, title, rest] = code_changes.split("\n\n", 2)

        pr_title = title.split('Title: ')[1]

        # Parse the generated code changes
        parsed_changes = parse_code_changes(rest)
        
        # Extract the pull request title
        # pr_title = parsed_changes.pop('Title', f'Address issue #{issue.number}')

        print("Ready to submit code changes")
        print(title)
        print(parsed_changes)
        
        # Create a new branch for the code changes
        new_branch = f"issue-{issue.number}"
        repo.create_git_ref(f'refs/heads/{new_branch}', repo.get_git_ref("refs/heads/main").object.sha)
        
        # Update the files with the generated code changes
        for filename, content in parsed_changes.items():
            file = repo.get_contents(filename, ref=new_branch)
            repo.update_file(
                path=f'{filename}',
                message=f'Update {filename} to address issue #{issue.number}',
                content=content,
                sha=file.sha,
                branch=new_branch,
            )
        
        # Create a new pull request
        repo.create_pull(
            title=pr_title,
            body=f'Address issue #{issue.number}',
            head=new_branch,
            base=repo.default_branch
        )
    else:
        print("Unable to parse final response")

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

    # Add initial context containing all the files in the repository
    context += "Existing files:\n"
    for file in repo.get_contents(''):
        if file.type == 'file':
            file_path = file.path
            file_contents = repo.get_contents(file_path).decoded_content.decode() 
            context += f'BEGIN FILE {file_path}\n{file_contents}\nEND FILE {file_path}\n\n'
    context += '\n'

    iterations = 0
    while iterations < 10:
        iterations += 1

        llm_prompt = "\n\n".join([
            " ".join([
                "You are operating as a standalone developer maintaining a code repository.",
                "You have received a code change request in the form of a GitHub Issue.",
                "You are tasked with generating a pull request that will resolve the issue.",
                "You are working within the scope of an existing code repository and you must review the existing code before suggesting changes.",
                "You may update as many files as necessary, including creating new files when needed.",
            ]),
            f"BEGIN CONTEXT\n{context}\nEND CONTEXT",
            f"Analyze the issue below and generate the appropriate code changes:\nBEGIN ISSUE\n{prompt}\nEND ISSUE",
            "\n\n".join([
                "Format your response as follows:",
                "CREATE PULL REQUEST",
                "Title: [Title of the pull request]",
                "\n".join([
                    BEGIN_FILE_CONTENTS+": [Path to the file]",
                    "[Full updated contents of the file with nothing omitted]",
                    "END FILE CONTENTS: [Path to the file]",
                ]),
                "\n".join([
                    BEGIN_FILE_CONTENTS+": [Path to another file]",
                    "[Full updated contents of another file with nothing omitted]",
                    "END FILE CONTENTS: [Path to another file]",
                ]),
                "\n".join([
                    BEGIN_FILE_CONTENTS+": [Path to a file to delete]",
                    "END FILE CONTENTS: [Path to a file to delete]",
                ])
            ])
        ])

        print("Request")
        print(llm_prompt)

        response = openai_client.chat.completions.create(
            model='hermes-3-llama-3.1-405b-fp8-128k',
            messages=[
                {
                    "role": "user",
                    "content": llm_prompt
                }
            ],
            max_tokens=10000,
            stream=True # Use streaming for easier monitoring and to avoid API timeouts
        )

        print("Response")

        # create variable to collect the stream of messages
        collected_messages = []
        # iterate through the stream of events
        for chunk in response:
            chunk_message = chunk.choices[0].delta.content  # extract the message
            collected_messages.append(chunk_message)  # save the message
            if chunk_message is not None:
                sys.stdout.write(chunk_message) # display the message
        print("") # add a final newline

        # clean None in collected_messages
        collected_messages = [m for m in collected_messages if m is not None]
        output = ''.join(collected_messages)

        # output = response.choices[0].message.content.strip()
        print("Full response")
        print(output)

        return output

    print("Ran out of iterations and terminated")

def parse_code_changes(code_changes):
    """
    Parse the generated code changes into a dictionary of filenames and their updated contents.
    """
    changes_dict = {}
    
    # Split the code changes into separate file updates
    d = BEGIN_FILE_CONTENTS+": "
    file_updates = [d+e for e in code_changes.split(d) if e]
    
    for update in file_updates:
        # Extract the filename and updated content
        if update.startswith(BEGIN_FILE_CONTENTS+': ') and "END FILE CONTENTS" in update:
            filename_start = update.index(BEGIN_FILE_CONTENTS+': ') + len(BEGIN_FILE_CONTENTS+': ')
            filename_end = update.index('\n', filename_start)
            filename = update[filename_start:filename_end].strip()
            
            content_start = filename_end + 1
            content_end = update.rfind('END FILE CONTENTS: '+filename)
            if(content_end < 0):
                print("Unable to locate end delimiter. Failing all parsing.")
                print(update)
                return {}
            content = update[content_start:content_end].strip()
            
            # Add the filename and content to the changes dictionary
            changes_dict[filename] = content
        else:
            print("Ignoring change for some reason")
            print(update)

    return changes_dict

# Unit tests
class TestGitHubBot(unittest.TestCase):
    # @patch.object(OpenAI, 'chat')
    # def test_rag_loop(self, mock_openai):
    #     # Test the RAG loop with a sample prompt and mocked OpenAI response
    #     prompt = "Add a new function to the utils.py file that calculates the factorial of a given number"
    #     mock_openai.completions.create.return_value = unittest.mock.Mock(choices=[unittest.mock.Mock(text="""Title: Add factorial function
        
    #     BEGIN FILE CONTENTS: utils.py
    #     def factorial(n):
    #         if n == 0:
    #             return 1
    #         else:
    #             return n * factorial(n - 1)
    #     END FILE CONTENTS
    #     """)])
        
    #     code_changes = rag_loop(prompt)
        
    #     # Assert that the code changes contain the expected function
    #     self.assertIn("def factorial(n):", code_changes)
    
    def test_parse_code_changes(self):
        # Test the parse_code_changes function with a sample output
        code_changes = BEGIN_FILE_CONTENTS+""": utils.py
# END FILE CONTENTS
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)
END FILE CONTENTS: utils.py"""
        
        parsed_changes = parse_code_changes(code_changes)
        
        # Assert that the parsed changes contain the expected filename and content
        self.assertIn("utils.py", parsed_changes)
        self.assertEqual(parsed_changes["utils.py"], """# END FILE CONTENTS
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)""")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Run the unit tests
        unittest.main(argv=[sys.argv[0]])
    else:
        # Run the bot
        print("Running")
        for issue in repo.get_issues():
            print("Handling an issue")
            if issue.state == 'open' and issue.comments == 0:
                process_issue(issue)

        for pr in repo.get_pulls():
            for comment in pr.get_comments():
                if comment.user != gh.get_user():
                    process_pull_request_comment(pr, comment)