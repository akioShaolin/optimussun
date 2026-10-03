import re
import unicodedata


def collapse_spaces(value):
    return re.sub(r"\s+", " ", str(value).strip())


def normalized_key(value):
    """Match utf8mb4_0900_ai_ci for the catalog's relevant Latin text."""
    collapsed = collapse_spaces(value).casefold()
    return "".join(
        char for char in unicodedata.normalize("NFKD", collapsed)
        if not unicodedata.combining(char)
    )

