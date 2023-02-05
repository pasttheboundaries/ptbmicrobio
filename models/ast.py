"""
ast  = antibiotic sensitivity testing
"""
from enum import Enum
from ptbmicrobio.common.validation import validate_type, validate_in
from ptbmicrobio.common.classes import TypeRestrictedList
from cantibiotics import antibiotic
from typing import Optional
from dataclasses import dataclass, field


SENSITIVITY_ENCODED = {'r': 0, 's': 1, 'i': 0.5, 'u': -1}


class Sensitivity(Enum):
    resistant = 'r'
    intermediate = 'i'
    sensitive = 's'
    unknown = 'u'

    @classmethod
    def polish(cls, s:str):
        translation = {'w':'s', 'o':'r'}
        validate_type(s, str, parameter_name='s')
        validate_in(s.lower(), tuple(translation.keys()))
        return cls(translation[s])

    @property
    def numeric(self):
        return SENSITIVITY_ENCODED[self.value]


class MIC(float):

    def __init__(self, v):
        if v not in (0.125, 0.25, 0.5, 1, 2, 4, 8):
            raise ValueError(f'Invalid MIC value {v}.')
        self.value = v
        super().__init__()

    def __repr__(self):
        return f'<MIC={self.value}>'


@dataclass(frozen=False)
class AntibioticSensitivity:
    antibiotic: str
    sensitivity: str
    mic: Optional[float] = field(default=None, compare=True)

    def __post_init__(self):
        validate_type(self.antibiotic, str, parameter_name='abx')
        validate_type(self.sensitivity, str, parameter_name='sens')
        self.antibiotic = antibiotic(self.antibiotic)
        self.sensitivity = Sensitivity(self.sensitivity)
        if self.mic:
            validate_type(self.mic, float, parameter_name='mic')
            self.mic = MIC(self.mic)


class AntibioticSensitivityList(TypeRestrictedList):
    CONTAINED_TYPE = AntibioticSensitivity


ASL = AntibioticSensitivityList