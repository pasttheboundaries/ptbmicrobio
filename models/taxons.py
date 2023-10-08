"""
this module defines basic taxon classes

"""
import pandas as pd
import numpy as np
from .interface import find, load_taxonomic_data
from itertools import chain
from collections.abc import Iterable
from typing import Union, NoReturn, Optional
from ptbmicrobio.common.validation import validate_type


def _flexible_return(array: Union[tuple, None], first: bool = None, last: bool = None) -> Union[tuple, NoReturn]:
    """
    returns passed iterable if it is truthy, otherwise returns None
    If parameter 'first' is set to True, than it returns first member of the iterable
    If parameter 'last' is set to True, than it returns last member of the iterable
    first has precedence over last if both are set to true
    """
    if not array:
        return None
    return (first and array[0]) or (last and array[-1]) or tuple(array)


class TaxonomicDataFrame(pd.DataFrame):
    """
    pandas.DataFrame wrapper for additional method get_taxons
    """
    def get_taxons(self, item):
        if item in self.columns:
            tax = TAXONS[item]
            applicable =[x for x in self[item].unique() if x is not np.nan]
            tax = sorted(list({tax(val) for val in applicable}), key=lambda x: repr(x))
            first = len(tax) == 1
            return _flexible_return(tax, first)
        return None


class Taxonomy:
    """
    descriptor for Taxon.taxonomy attribute
    Extractes rows matching the Taxon instance and wraps them in TaxonomicalDataFrame
    so further taxon of kin can be extraxted
    like in:
    t = Taxon('salmonella')
    tax = t.taxonomy  # type:TaxonomicDataFrame
    tax.genus -> list of related genus or instance of genus
    """
    data = load_taxonomic_data()

    def __init__(self):
        self.td = load_taxonomic_data()

    def __get__(self, instance, owner):
        return self.find_branches(instance)

    @staticmethod
    def find_branches(taxon):
        # col = taxon.__class__.__name__.lower()
        col = taxon.__class__.__name__
        rows = Taxonomy.data[Taxonomy.data[col] == taxon.name]
        rows = rows.reset_index(drop=True)
        return TaxonomicDataFrame(rows)


class Taxon:
    """
    Base class for other taxon classes.
    Also used as an entry point for taxon search with Taxon.find() class method.

    """
    taxonomy = Taxonomy()

    def __init__(self, name: str):
        validate_type(name, str, parameter_name='name')
        self.name = name

    def __getattr__(self, item: str):
        validate_type(item, str, parameter_name='item')
        if item in TAXONS:
            return self.taxonomy.get_taxons(item)
        return self.__getattribute__(item)

    def __hash__(self):
        return hash(str(id(self)))

    def __eq__(self, other):
        validate_type(other, Taxon, parameter_name='other', error_message=f'Could not compare Taxon to {type(other)}')
        return repr(self) == repr(other)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name}>'

    @staticmethod
    def _instantiate_found(taxon_cls, dfs, col) -> Union[None, tuple]:
        if dfs is None or len(dfs) == 0:
            return None
        else:
            return tuple(instance for df in dfs for instance in taxon_cls._instantiate_from_df(taxon_cls, df, col) if instance)

    @staticmethod
    def _instantiate_from_df(taxon_cls, df, col) -> tuple:
        if df is None or len(df) == 0 or col not in df.columns:
            return tuple()
        else:
            return tuple(taxon_cls(name) for name in df[col])


    @classmethod
    def find(cls, value=None, strict=True, first=False, last=False, force=False):
        if cls == Taxon:
            """
            if Taxin.find is used
            (if find.Taxon is used the code searching for any is in interface.TaxonQuery)
            """
            li = [tax.find(value, strict, force=force) for tax in TAXONS.values()]
            li = [member for member in li if member]
            return _flexible_return(tuple(chain(*li)), first, last)
        else:
            # col = cls.__name__.lower()
            col = cls.__name__
            rows = find(col)(value, strict=strict, force=force)
            result = cls._instantiate_found(cls, rows, col)
            return _flexible_return(result, first, last)

    @property
    def valid(self):
        try:
            return bool(self.domain)
        except AttributeError:
            return False


class Domain(Taxon):
    pass


class Phylum(Taxon):
    pass


class Class(Taxon):
    pass


class Order(Taxon):
    pass


class Family(Taxon):
    pass


class Genus(Taxon):
    pass


class Species(Taxon):
    pass


TAXONS = {t.__name__: t for t in Taxon.__subclasses__()}
