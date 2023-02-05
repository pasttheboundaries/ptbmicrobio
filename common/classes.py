from collections import UserList
from typing import Any


class TypeRestrictedList(UserList):
    CONTAINED_TYPE = object

    def _validate_value(self, value: Any) -> Any:
        if not isinstance(value, self.CONTAINED_TYPE):
            cls_name = self.__class__.__name__
            raise TypeError(f'{cls_name} can not contain type {type(value)}. '
                            f'Valid type is {self.__class__.CONTAINED_TYPE}.')
        return value

    def append(self, value: Any):
        return super().append(self._validate_value(value))

    def insert(self, ind: int, value: Any):
        super().insert(ind, self._validate_value(value))

    def __setitem__(self, key: int, value: Any) -> None:
        super().__setitem__(key, self._validate_value(value))