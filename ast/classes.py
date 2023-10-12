from collections import UserDict
from collections.abc import Iterable
from typing import Mapping
import json
from enum import Enum


class Resistance(Enum):
    resistant = 1
    sensitive = -1
    intermediate = 0.5
    unknown = 0


class AST(UserDict):
    def __init__(self, ast=None):
        super().__init__()
        if ast:
            self._load_ast(ast)
    @staticmethod
    def _validate_value(val):
        val = SensitivityReadout(val)
        return val

    def _validate_key(self, key):
        if not isinstance(key, str):
            raise TypeError(f'key must be a str type.')
        return key

    def update(self, __m: Mapping, **kwargs) -> None:
        if isinstance(__m, (dict, AST)):
            self._iter_update_items(__m.items())
        else:
            raise TypeError('AST can only accept other AST or a dict')
        self._iter_update_items(kwargs.items())

    def _iter_update_items(self, items):
        for k, v in items:
            self[self._validate_key(k)] = self._validate_value(v)

    def _load_ast(self, ast):
        self.update(ast)

    @classmethod
    def from_dict(cls, d: dict):
        return AST(d)

    @classmethod
    def from_json(cls, js: str):
        return AST(json.loads(js))

    def __repr__(self):
        return f'<AST {dict(self)}>'


class SensitivityReadout(tuple):
    """
    (resistance_categorical, MIC)
    """
    def __init__(self, seq=()):
        if seq and not isinstance(seq, Iterable):
            raise TypeError(f'Tried to pack a SensitivityReadout but got a non iterable type: {type(seq)}')

        super().__init__()
        if len(self) != 2:
            raise ValueError('SensitivityReadout object must always contain 2 items.')

    def __repr__(self):
        return f'<{self.__class__.__name__} {tuple(self)}>'
