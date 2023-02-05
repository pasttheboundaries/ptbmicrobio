
from enum import Enum


class Sensitivity(Enum):
    resistant = 'r'
    intermediate = 'i'
    sensitive = 's'


class MIC(float):
    def __init__(self, v):
        if not v in (0.125, 0.25, 0.5, 1, 2, 4, 8):
            raise ValueError(f'Invalid MIC value {v}.')
        self.v = v
        super().__init__()


    def __repr__(self):
        return f'<MIC={self.v}>'



