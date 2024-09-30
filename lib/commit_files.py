from .github import repo
from .log import log

def commit_files(branch, files, reason=" just because"):
        # Update the files with the generated code changes
        for filename, content in files.items():
            if content.strip() == "":
                # Delete the file if the content is empty, but only if it previously existed
                try:
                    file = repo.get_contents(filename, ref=branch)
                    log(f"Deleting empty file: {filename}")
                    repo.delete_file(
                        path=filename,
                        message=f"Delete {filename}{reason}",
                        branch=branch,
                        sha=file.sha,
                    )
                except:
                     log(f"Creating empty file: {filename}")
                     repo.create_file(
                        path=f'{filename}',
                        message=f'Create {filename}{reason}',
                        content=content,
                        branch=branch,
                    )
            else:
                try:
                    file = repo.get_contents(filename, ref=branch)
                    log(f"Updating file: {filename}")
                    repo.update_file(
                        path=f'{filename}',
                        message=f'Update {filename}{reason}',
                        content=content,
                        sha=file.sha,
                        branch=branch,
                    )
                except:
                    log(f"Creating file: {filename}")
                    repo.create_file(
                        path=f'{filename}',
                        message=f'Create {filename}{reason}',
                        content=content,
                        branch=branch,
                    )