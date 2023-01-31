"""
this module provides classes and methods neccesary for searching data in source DataFrame
"""
from ptbmicrobio.common.data import bacteria_species


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

    def find_taxon(self, column, value, strict=True):
        """
        finds matching taxon name in one column of the input dataframe
        """
        value_low = value.lower()
        matching = [name for name in self.df[column].unique() if self._match(value_low, name.lower(),strict=strict )]
        if matching:
            rows = self.df[self.df[column].apply(lambda x: x in matching)]
            rows = rows.loc[:, : column].drop_duplicates().reset_index()
            return rows
        else:
            return None

    def find_any(self, value, strict=True):
        dfs = [self.find_taxon(column, value, strict=strict) for column in self.df.columns]
        dfs = [df for df in dfs if df is not None and df.size > 0]
        return dfs or None

    def __call__(self, value, strict=True):
        if self.column in self.df.columns:
            return self.find_taxon(self.column, value, strict=strict)
        else:
            return self.find_any(value, strict=strict)


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

    def __call__(self, item, strict=True):
        item = item in self.df.columns and item or None
        return TaxonQuery(self.df, item, strict=strict)


find = TaxonomyFinder(bacteria_species)


