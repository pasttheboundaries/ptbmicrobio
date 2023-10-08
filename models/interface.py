"""
this module provides classes and methods neccesary for searching pairs_generator in source DataFrame
"""
import pandas as pd
import numpy as np
from ptbmicrobio.common.data import load_taxonomic_data
from typing import Union, List


class TaxonQuery:
    """
    Auxiliary class
    allowing for best match search and also search in all source dataframe if condition is met (invalid column is used)
    It serves basically as code organiser.

    TaxonQuery is a callable within a desired column of the cource DataFrame
    It also can search all the DataFrame.
    When called returns a list of dataframe slices
    """
    def __init__(self, df, column=None, strict=True):
        self.df = df
        self.column = column
        self.strict = strict

    @staticmethod
    def _match(s1, s2, strict):
        if strict:
            return s1 == s2
        return s1 in s2

    def find_taxon(self, column, value, strict=True) -> Union[pd.DataFrame, None]:
        """
        finds matching value in one column of the input dataframe
        and returns all aplicable rows OR None
        """
        #print(f'taxon {self.column} finding {value} in column {column}')
        names = self.df[column].dropna().unique()
        matching = [name for name in names if self._match(value.lower(), name.lower(), strict=strict)]
        if matching:
            rows = self.df[self.df[column].apply(lambda x: x in matching)]
            rows = rows.loc[:, : column].drop_duplicates().reset_index(drop=True)
            return rows
        else:
            return None

    def find_any(self, value, strict=True) -> List[pd.DataFrame]:
        """
        finds value in all columns of the self.df and returns in a list of DataFrameSLices
        """
        dfs = [self.find_taxon(column, value, strict=strict) for column in self.df.columns]
        dfs = [df for df in dfs if df is not None and df.size > 0]
        return dfs

    @staticmethod
    def _preprocess_value(value):
        spl = value.split(' ')
        if len(spl) > 2:
            spl = spl[:2]
        if len(spl) == 2 and spl[1].lower() in ('species', 'sp', 'sp.'):
            spl = spl[:1]
        return ' '.join(spl)

    def __call__(self, value, strict=True, force=False) -> List[pd.DataFrame]:
        """
        :param value: str
        :param strict: bool -valu comparison either "==" or "in"
        :param force: bool - experimental
        :return:
        """
        value = self._preprocess_value(value)
        if self.column in self.df.columns:
            returnable = self.find_taxon(self.column, value, strict=strict)
            if returnable is not None:
                returnable = [returnable]
            else:
                returnable = []
        elif self.column is None:
            """
            if find.taxon is used this searches for any taxon
            (if Taxon.find is used the search for any taxon is coded in Taxon class)
            """
            returnable = self.find_any(value, strict=strict)
        else:
            raise ValueError(f'TaxonQuery instantiated with wrong taxon name. Got {self.column}. '
                             f'Expected one of {tuple(self.df.columns)}')
        if force and not returnable:
            chunks = value.split(' ')[:-1]
            if not chunks:  # recursion stop
                returnable = []
            else:
                value = ' '.join(chunks)
                returnable = self(value, strict=strict, force=True)
        return returnable


class TaxonQueryConstructor:
    """TaxonQueryConstructor
    this class instance delivers 2 functionalities:
    1) it works on its own as an independant object.
    Its attributes are projected to source dateframe columns when creating TexonQuery
    TaxonFinder(df).Genus -> TaxonQuery instance working in df['Genus']
    2) is callable so can be used with source dataframe column insted:
    TaxonFinder(df)('Genus') -> TaxonQuery instance working in df['Genus']
    """
    def __init__(self, df):
        self.df = df

    def __getattr__(self, taxon_name):
        return self(taxon_name) or self.__getattribute__(taxon_name)

    def __call__(self, item, strict=True) -> TaxonQuery:
        item = item in self.df.columns and item or None
        return TaxonQuery(self.df, item, strict=strict)


find = TaxonQueryConstructor(load_taxonomic_data())


