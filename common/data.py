"""
this modlule reads source DataFrame
"""


import os
import pandas as pd
from ptbmicrobio import LOCAL_PATH
from collections import Iterable

TAXONOMIC_DATA_PATH = os.path.join(LOCAL_PATH, 'data', 'bacteria.csv')

taxonomic_data = pd.read_csv(TAXONOMIC_DATA_PATH)


def _flexible_return(array: Iterable, first: bool) -> tuple:
    """
    returns passed iterable if it is truthy, otherwise returns None
    If parameter 'first' is set to True, than it returns first member of the iterable
    """
    if not array:
        return None
    return first and array[0] or tuple(array)


class TaxonomicDataFrame(pd.DataFrame):
    """
    pandas.DataFrame wrapper for additional method get_taxons
    """
    def get_taxons(self, item):
        if item in TAXONS and item in self.columns:
            tax = TAXONS[item]
            tax = sorted(list({tax(val) for val in self[item].unique()}), key=lambda x: repr(x))
            first = len(tax) == 1
            return _flexible_return(tax, first)
        return None
