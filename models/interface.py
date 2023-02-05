"""
this module provides classes and methods neccesary for searching data in source DataFrame
"""
import pandas as pd
from ptbmicrobio.common.data import taxonomic_data
from typing import Union


class TaxonQuery:
    """
    Auxiliary class
    allowing for best match search and also search in all source dataframe if condition is met (invalid column is used)
    It serves basically code organisation.
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
        """
        value_low = value.lower()
        matching = [name for name in self.df[column].unique() if self._match(value_low, name.lower(),strict=strict )]
        if matching:
            rows = self.df[self.df[column].apply(lambda x: x in matching)]
            rows = rows.loc[:, : column].drop_duplicates().reset_index()
            return rows
        else:
            return None

    def find_any(self, value, strict=True) -> Union[list, None]:
        """
        finds value in all columns of the self.df and returns in a list
        """
        dfs = [self.find_taxon(column, value, strict=strict) for column in self.df.columns]
        dfs = [df for df in dfs if df is not None and df.size > 0]
        return dfs or None

    @staticmethod
    def _preprocess_value(value):
        spl = value.split(' ')
        if len(spl) > 2:
            spl = spl[:2]
        if len(spl) == 2 and spl[1].lower() in ('species', 'sp', 'sp.'):
            spl = spl[:1]

        return ' '.join(spl)

    def __call__(self, value, strict=True, force=True) -> Union[list, pd.DataFrame, None]:
        value = self._preprocess_value(value)

        if self.column in self.df.columns:
            returnable =  self.find_taxon(self.column, value, strict=strict)

        else:
            returnable = self.find_any(value, strict=strict)

        if force and returnable is None:
            value = value.split(' ')[0]
            returnable = self(value, strict=strict, force=False)

        return returnable


class TaxonomyFinder:
    """
    this class instance delivers 2 functionalities:
    1) it works on its own as an independant object. Ist attributes are projected to source dateframe columns when creatin TexonQuery
    TaxonFinder(df).genus -> TaxonQuery instance working in df['genus']
    2) is callable so can be used with source dataframe column insted:
    TaxonFinder(df)('genus') -> TaxonQuery instance working in df['genus']
    """
    def __init__(self, df):
        self.df = df

    def __getattr__(self, item):
        return self(item) or self.__getattribute__(item)

    def __call__(self, item, strict=True) -> TaxonQuery:
        item = item in self.df.columns and item or None
        return TaxonQuery(self.df, item, strict=strict)


find = TaxonomyFinder(taxonomic_data)


