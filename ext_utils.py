import re

def is_already_completed(page_content: str) -> bool:
    return re.search(r"You have finished test", page_content, re.IGNORECASE) is not None or \
            re.search(r"Test completed", page_content, re.IGNORECASE) is not None or \
            re.search(r"automatically finished", page_content, re.IGNORECASE) is not None