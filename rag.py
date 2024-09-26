import logging
from openai import OpenAI

# Special keyword that can never appear in the code or it breaks the self-management behavior
# Reason: we split files in the LLM output on this keyword, so it should only exist in the LLM "meta" output
SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER = " ".join(["###","BEGIN","FILE","CONTENTS"])

openai_client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

def rag_loop(prompt, extra_context):
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
            stream=True # Use streaming for easier monitoring and to avoid API timeouts
        )

        log("Response")

        # create variable to collect the stream of messages
        collected_messages = []
        # iterate through the stream of events
        for chunk in response:
            chunk_message = chunk.choices[0].delta.content  # extract the message
            collected_messages.append(chunk_message)  # save the message
            if chunk_message is not None:
                sys.stdout.write(chunk_message) # display the message
        sys.stdout.write("\n") # add a final newline

        # clean None in collected_messages
        collected_messages = [m for m in collected_messages if m is not None]
        output = ''.join(collected_messages)

        # output = response.choices[0].message.content.strip()
        log("Full response")
        log(output)

        return output

    log("Ran out of iterations and terminated")

def parse_code_changes(code_changes):
    """
    Parse the generated code changes into a dictionary of filenames and their updated contents.
    """
    changes_dict = {}
    
    # Split the code changes into separate file updates
    d = SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER+": "
    file_updates = [(d+e).strip() for e in ("\n"+code_changes).split("\n"+d) if e]
    
    for update in file_updates:
        # Extract the filename and updated content
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
            
            # Add the filename and content to the changes dictionary
            changes_dict[filename] = content
        else:
            log("Ignoring change for some reason")
            log(update)

    return changes_dict