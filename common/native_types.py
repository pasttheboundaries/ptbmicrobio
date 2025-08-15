from collections import namedtuple
import pandas as pd
from .ptbserialization import PtbSerializable


class ParsedData:
    """
    ADB loaded and parsed data
    """
    pass


@PtbSerializable.register
class ParsedCultureResult(ParsedData, list):
    def serialization_init_params(self):
        return list(self)

    def serialization_instance_attrs(self):
        pass


@PtbSerializable.register
class ParsedCulture(ParsedData, dict):
    def serialization_init_params(self):
        return dict(self)

    def serialization_instance_attrs(self):
        pass


class ParsedDataFrame(ParsedData, pd.DataFrame):
    pass


@PtbSerializable.register
class AST(ParsedData, dict):  #antibiotic sensitivity testing
    def __repr__(self):
        return f'<AST {dict(self)}>'

    def serialization_init_params(self):
        return dict(self)

    def serialization_instance_attrs(self):
        pass

@PtbSerializable.register
class SensitivityReadout(namedtuple('SensitivityReadout', field_names=('resistance', 'mic'))):
    """
    (resistance_categorical, MIC)
    """

    def __repr__(self):
        return f'<{self.__class__.__name__} resistance:{self.resistance}, mic:{self.mic}>'

    def serialization_init_params(self):
        return {'*': tuple(self)}

    def serialization_instance_attrs(self):
        pass