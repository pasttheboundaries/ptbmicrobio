import re
from unicodedata import normalize as unorm


def normalize_text(text: str) -> str:
    """
    performs text normalization:
    - normalizes unicode
    - replaces whitespace characters with notrmal space - this also considers special sighs like \n
    - replaces multiple spaces with one space
    """
    return shrink_spaces(whitespace_to_space(normalize_unicode(replace_punctuation(text))))


def shrink_spaces(text: str) -> str:
    return ' '.join(text.split())


def normalize_unicode(text):
    """normalizes unicode chars"""
    return unorm('NFKC', text)


def whitespace_to_space(text):
    return re.sub(r'[^\S\r\n]', ' ', text)


def replace_punctuation(text: str) -> str:
    return re.sub(r'\W', ' ', text)


def rotate_chunk_pairs(text):
    chunks = text.split(' ')
    if len(chunks) < 2:
        return
    else:
        for i in range(len(chunks) - 1):
            yield chunks[i: i + 2]
