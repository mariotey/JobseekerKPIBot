import re

TAG_PATTERN = r"#\w+"


def extract_tag(text: str):
    if not text:
        return None

    matches = re.findall(TAG_PATTERN, text)

    if len(matches) != 1:
        return None

    return matches[0].lower()