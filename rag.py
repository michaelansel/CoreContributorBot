import logging
from openai import OpenAI
import os
import sys
from github import Github

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log(message):
    logging.info(message)

openai_api_key = os.environ['OPENAI_API_KEY']
openai_api_base = "https://api.lambdalabs.com/v1"

openai_client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER = " ".join(["###","BEGIN","FILE","CONTENTS"])

def process_issue(issue):
    code_changes = rag_loop(f'Title: {issue.title}\nDescription:\n{issue.body}', "")
    
    if code_changes and code_changes.startswith("CREATE PULL REQUEST"):
        [cpr, title, rest] = code_changes.split("\n\n", 2)
        pr_title = title.split('Title: ')[1]
        parsed_changes = parse_code_changes(rest)
        
        new_branch = f"issue-{issue.number}"
        repo.create_git_ref(f'refs/heads/{new_branch}', repo.get_git_ref("heads/main").object.sha)
        
        for filename, content in parsed_changes.items():
            try:
                file = repo.get_contents(filename, ref=new_branch)
                repo.update_file(
                    path=f'{filename}',
                    message=f'Update {filename} to address issue #{issue.number}',
                    content=content,
                    sha=file.sha,
                    branch=new_branch,
                )
            except:
                repo.create_file(
                    path=f'{filename}',
                    message=f'Update {filename} to address issue #{issue.number}',
                    content=content,
                    branch=new_branch,
                )
        
        pr = repo.create_pull(
            title=pr_title,
            body=f'Address issue #{issue.number}',
            head=new_branch,
            base=repo.default_branch
        )

        issue.create_comment(f"Bot Response: Handling in PR: {pr.html_url}")
    else:
        log("Unable to parse final response")

def process_pull_request_comment(pr, comment):
    issue_title, issue_description = extract_issue_from_pull_request(pr.body)
    proposed_changes = get_proposed_changes(pr)

    extra_context = ""
    extra_context += f"Issue Title: {issue_title}\nIssue Description:\n{issue_description}\n\n"
    extra_context += "Proposed Changes:\n"
    for filename, patch in proposed_changes.items():
        extra_context += f"BEGIN FILE {filename}\n{patch}\nEND FILE {filename}\n"
    extra_context += '\n'

    code_changes = rag_loop(comment.body, extra_context)
    
    if code_changes:
        latest_commit = pr.get_commits().reversed[0]
        
        pr_branch = pr.head.ref
        for filename, content in parse_code_changes(code_changes).items():
            try:
                file = repo.get_contents(filename, ref=pr_branch)
                repo.update_file(
                    path=f'{filename}',
                    message=f'Update {filename} based on feedback',
                    content=content,
                    sha=file.sha,
                    branch=pr_branch,
                )
            except:
                repo.create_file(
                    path=f'{filename}',
                    message=f'Update {filename} based on feedback',
                    content=content,
                    branch=pr_branch,
                )

        pr.create_issue_comment("Bot Response: Updated based on feedback")

def extract_issue_from_pull_request(pr_body):
    if pr_body.startswith("Address issue #"):
        number = pr_body.split("Address issue #", 1)[1]
        issue = repo.get_issue(number=int(number))
        return issue.title, issue.body
    
    raise Exception("can't find the associated issue")

def get_proposed_changes(pr):
    proposed_changes = {}
    for file in pr.get_files():
        proposed_changes[file.filename] = file.patch
    return proposed_changes

def rag_loop(prompt, extra_context):
    context = ''

    context += "Existing files:\n"
    for file in repo.get_contents(''):
        if file.type == 'file':
            file_path = file.path
            file_contents = repo.get_contents(file_path).decoded_content.decode() 
            context += f'BEGIN FILE {file_path}\n{file_contents}\nEND FILE {file_path}\n\n'
    context += '\n'

    context += extra_context

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
                    SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER+": [Path to the file]",
                    "[Full updated contents of the file with nothing omitted]",
                    "END FILE CONTENTS: [Path to the file]",
                ]),
                "\n".join([
                    SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER+": [Path to another file]",
                    "[Full updated contents of another file with nothing omitted]",
                    "END FILE CONTENTS: [Path to another file]",
                ]),
                "\n".join([
                    SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER+": [Path to a file to delete]",
                    "END FILE CONTENTS: [Path to a file to delete]",
                ])
            ])
        ])

        log("Request")
        log(llm_prompt)

        response = openai_client.chat.completions.create(
            model='hermes-3-llama-3.1-405b-fp8-128k',
            messages=[
                {
                    "role": "user",
                    "content": llm_prompt
                }
            ],
            max_tokens=10000,
            stream=True
        )

        log("Response")

        collected_messages = []
        for chunk in response:
            chunk_message = chunk.choices[0].delta.content
            collected_messages.append(chunk_message)
            if chunk_message is not None:
                sys.stdout.write(chunk_message)
        sys.stdout.write("\n")

        collected_messages = [m for m in collected_messages if m is not None]
        output = ''.join(collected_messages)

        log("Full response")
        log(output)

        return output

    log("Ran out of iterations and terminated")

def parse_code_changes(code_changes):
    changes_dict = {}
    
    d = SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER+": "
    file_updates = [(d+e).strip() for e in ("\n"+code_changes).split("\n"+d) if e]
    
    for update in file_updates:
        if update.startswith(SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER+': ') and "END FILE CONTENTS" in update:
            filename_start = update.index(SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER+': ') + len(SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER+': ')
            filename_end = update.index('\n', filename_start)
            filename = update[filename_start:filename_end].strip()
            
            content_start = filename_end + 1
            content_end = update.rfind('END FILE CONTENTS: '+filename)
            if(content_end < 0):
                log("Unable to locate end delimiter. Failing all parsing.")
                log(update)
                return {}
            content = update[content_start:content_end].strip()
            
            changes_dict[filename] = content
        else:
            log("Ignoring change for some reason")
            log(update)

    return changes_dict