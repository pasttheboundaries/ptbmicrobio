"""
this module provides classes and methods neccesary for searching pairs_generator in source DataFrame
"""
import pandas as pd
from ..common.data import load_taxonomic_data
from typing import Union, List
from functools import lru_cache


class TaxonQuery:
    """
    Auxiliary class
    allowing for best match search and also search in all source dataframe if condition is met (invalid column is used)
    It serves basically as code organiser.

    TaxonQuery is a callable within a desired column of the cource DataFrame
    It also can search all the DataFrame.
    When called returns a list of dataframe slices
    """
    def __init__(self, df, column=None, partial=True):
        self.df = df
        self.column = column
        self.partial = partial

    @staticmethod
    def _match(s1, s2, partial):
        if partial:
            return s1 in s2
        return s1 == s2

    @lru_cache(maxsize=100)
    def find_taxon(self, column, value, partial=True) -> Union[pd.DataFrame, None]:
        """
        finds matching value in one column of the input dataframe
        and returns all aplicable rows OR None
        """
        #print(f'taxon {self.column} finding {value} in column {column}')
        names = self.df[column].dropna().unique()
        matching = [name for name in names if self._match(value.lower(), name.lower(), partial=partial)]
        if matching:
            rows = self.df[self.df[column].apply(lambda x: x in matching)]
            rows = rows.loc[:, : column].drop_duplicates().reset_index(drop=True)
            return rows
        else:
            return None

    def find_any(self, value, partial=True) -> List[pd.DataFrame]:
        """
        finds value in all columns of the self.df and returns in a list of DataFrameSLices
        """
        dfs = [self.find_taxon(column, value, partial=partial) for column in self.df.columns]
        dfs = [df for df in dfs if df is not None and df.size > 0]
        return dfs

    @lru_cache(maxsize=100)
    def __call__(self, value, partial=True, force=False) -> List[pd.DataFrame]:
        """
        :param value: str
        :param partial: bool -value comparison either "==" or "in"
        :param force: bool - experimental
        :return: a list of matching DataFrame rows
        """

        returnable = []
        if self.column in self.df.columns:
            df = self.find_taxon(self.column, value, partial=partial)
            if df is not None:
                returnable = [df]

        elif self.column is None:
            """
            if find.taxon is used this searches for any taxon
            (if Taxon.find is used the search for any taxon is coded in Taxon class)
            """
            returnable = self.find_any(value, partial=partial)
        else:
            raise ValueError(f'TaxonQuery instantiated with wrong taxon name. Got {self.column}. '
                             f'Expected one of {tuple(self.df.columns)}')
        if force:
            """
            NOT IMPLEMENTED
            this logic should force search within a specific column (taxon) 
            as looping over columns (taxons) is performed by Taxon.find
            SO
            this logic should actually search similarity in strings only
            """
            pass
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

    def __call__(self, column, partial=True) -> TaxonQuery:
        column = column in self.df.columns and column or None
        return TaxonQuery(self.df, column, partial=partial)


find = TaxonQueryConstructor(load_taxonomic_data())


