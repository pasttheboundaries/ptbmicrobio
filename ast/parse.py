"""
IN DEVELOPMENT


przepis
ustal re dla mic
ustal re dla klasyfikacji wrażliwości
ustal re dla antybiotyku
ustal re dla nagłówka
ustal re dla stopki


"""

import re
from typing import Optional
from ..common.decorators import experimental


MIC_PATTERN = r'(?i)\smic[\s\W]'
POSTMIC_PATTER = r'[\s\W]*(?=\d{1,2}([,.]\d{1,2})?)'
DIGIT_PATTERN =r'\d{1,2}([,.]\d{1,2})?'
DIGIT_SPLIT_PATTERN = r'\d{1,2}[,.]\d{1,2}|\d{1,2}'
CHUNKING_PATTERN = r'\s|\W(?!\d)'


@experimental
class ASTParser:
    def __init__(self, re_pattern: Optional[str] = None):
        self.re_pattern = re_pattern
        self.mypattern = r''
        self.mic_pattern = r''

    def parse(self, s):
        s = self._validate_string(s)
        s = self._reorganise_s(s)
        return s

    def _validate_string(self, s):
        if not isinstance(s, str):
            raise TypeError(f'Expected string. Got {type(s)}.')
        if len(s) < 20:
            raise NotImplementedError(f'Too short to by AST string: {s}')
        return s

    def _reorganise_s(self, s):
        s = re.split(CHUNKING_PATTERN, s)
        s = (e for e in s if e)
        return ' '.join(s)


@experimental
class MicSplitFinder(ASTParser):
    def __init__(self, re_pattern: Optional[str] = None):
        self.re_pattern = re_pattern
        self.pre_mic_pattern = r''
        self.mic_pattern = r''
        self.post_mic_pattern = r''

    def parse(self, s):
        s = self._validate_string(s)

    def _search_mic_pattern(self, s):
        """
        finds pattern: (MIC:    )
        """
        chunks = re.split(MIC_PATTERN,s)
        if len(chunks) == 1:
            return self._search_number_no_mic(s)

    def _search_number_no_mic(self, s):
        """
        finds pattern (  0,5)
        """
        chunks = re.split(DIGIT_SPLIT_PATTERN, s)
        if len(chunks) == 1:
            return

    def _search_postmic_spaces_pattern(self, chunks):
        posts = (re.search(POSTMIC_PATTER, ch).group() for ch in chunks[1:])
        if all(isinstance(p, str) for p in posts):
            lengths = {len(p) for p in posts}
            self.post_mic_pattern = r'{' + rf'{min(lengths)},{max(lengths)}' + r'}'

        else: # some are None
            pass

    def _search_postdigit_spaces_pattern(self, chunks):
        posts = (re.search(POSTMIC_PATTER, ch).group() for ch in chunks[1:])
        if all(isinstance(p, str) for p in posts):
            lengths = {len(p) for p in posts}
            self.post_mic_pattern = r'{' + rf'{min(lengths)},{max(lengths)}' + r'}'

        else: # some are None
            pass








