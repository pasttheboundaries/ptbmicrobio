from collections import UserDict
from typing import Mapping, Iterable
import json
from enum import Enum
from collections import namedtuple


class ResistanceFlag(Enum):
    resistant = 1
    sensitive = 0
    intermediate = 0.5
    unknown = None


class AST(dict):
    def __init__(self, ast=None):
        super().__init__()
        if ast:
            self.update(ast)

    @staticmethod
    def _validate_value(val: Iterable):
        val = SensitivityReadout(*val)
        return val

    @staticmethod
    def _validate_key(key: str):
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

    @classmethod
    def from_dict(cls, d: dict):
        return AST(d)

    @classmethod
    def from_json(cls, js: str):
        return AST(json.loads(js))

    def to_dict(self):
        return {k: tuple(v) for k, v in self.items()}

    def __repr__(self):
        return f'<AST {dict(self)}>'


class SensitivityReadout(namedtuple('SensitivityReadout', field_names=('resistance', 'mic'))):
    """
    (resistance_categorical, MIC)
    """

    def __repr__(self):
        return f'<{self.__class__.__name__} resistance:{self.resistance}, mic:{self.mic}>'
