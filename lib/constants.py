# Define special constants used in the codebase
# Special keyword that can never appear in the code or it breaks the self-management behavior
# Reason: we split files in the LLM output on this keyword, so it should only exist in the LLM "meta" output
SPECIAL_BEGIN_FILE_CONTENTS_DELIMETER = " ".join(["###","BEGIN","FILE","CONTENTS"])