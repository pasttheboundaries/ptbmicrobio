"""
this module defines basic taxon classes

"""
import pandas as pd
import numpy as np
from functools import lru_cache
from .interface import find, load_taxonomic_data
from itertools import chain
from typing import Union, NoReturn, TypeVar, Generic
from ..common.validation import validate_type
from ..extraction.functions import normalize_text, rotate_chunk_pairs


T = TypeVar('T', bound='MyClass')
EMPTY = tuple()


def _flexible_return(collection: Union[tuple, None], first: bool = False, last: bool = False) -> Union[tuple, NoReturn]:
    """
    returns passed iterable if it is truthy, otherwise returns None
    If parameter 'first' is set to True, than it returns first member of the iterable
    If parameter 'last' is set to True, than it returns last member of the iterable
    first has precedence over last if both are set to True
    """
    if not collection:
        if first or last:
            return None
        else:
            return EMPTY
    else:
        return (first and collection[0]) or (last and collection[-1]) or tuple(collection)


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


class Taxon(Generic[T]):
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
        # this was hashed out as unnecessarily restrictive
        # validate_type(other, Taxon, parameter_name='other', error_message=f'Could not compare Taxon to {type(other)}')
        try:
            return (self.__class__, self.name) == (other.__class__, other.name)
        except AttributeError:
            return False

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name}>'

    def __str__(self):
        return self.name

    @staticmethod
    def _instantiate_found(taxon_cls, dfs, col) -> Union[None, tuple]:
        if dfs is None or len(dfs) == 0:
            return tuple()
        else:
            return tuple(i for df in dfs for i in taxon_cls._instantiate_from_df(taxon_cls, df, col) if i)

    @staticmethod
    def _instantiate_from_df(taxon_cls, df, col) -> tuple:
        if df is None or len(df) == 0 or col not in df.columns:
            return EMPTY
        else:
            return tuple(taxon_cls(name) for name in df[col])

    @classmethod
    @lru_cache(maxsize=100)
    def find(cls,
             value=None,
             partial=False,
             first=False, last=False,
             force=False, progressive=False, ) -> Union[tuple, T, NoReturn]:
        """

        :param value: bacteria name
        :param partial: matching mode, if partial is True, partial match will be checked
        :param first: in Taxon.find (but not sublcasses) - if multiple results are found , the first one is returned
        :param last: in Taxon.find (but not sublcasses) - if multiple results are found , the last one is returned
        first has precedense over last
        :param force: not implemented - this parameter is passed to TaxonQuery object
        :param progressive: in Taxon.find (but not sublcasses) - performs input string chunkation and progressive search
        if set to True , than search is able to omit insignificant words in the string.
        :return:
        """
        value = normalize_text(value)
        if cls == Taxon:
            return cls.find_any(value=value,
                                partial=partial,
                                first=first, last=last,
                                force=force, progressive=progressive)
        else:
            return cls.find_specific(value=value, partial=partial, force=force,
                                     first=first, last=last, progressive=progressive)

    @classmethod
    def find_any(cls,
                 value=None,
                 partial=False,
                 first=False, last=False,
                 progressive=False, force=False) -> Union[tuple, T, NoReturn]:

        if not progressive:
            li = [tax.find(value, partial=partial, force=force, first=False) for tax in TAXONS.values()]
            li = [m for m in li if m]

        else:
            li = cls.taxon_progressive_find(value=value, partial=partial, force=force)
        return _flexible_return(tuple(chain(*li)), first, last)

    @classmethod
    def taxon_progressive_find(cls, value, partial=False, force=False) -> list[tuple]:
        li = list()

        # find species using 2 chunks
        li.append(Species.species_progressive_find(value, partial=partial, force=force))

        # find other taxons using single chunks
        non_g_taxons = [t for t in TAXONS.values() if t != Species]
        for tax in non_g_taxons:
            li.append(tax.nonspecies_progressive_find(value, partial=partial, force=force))
        li = [m for m in li if m]
        return li

    @classmethod
    def species_progressive_find(cls, value, partial=False, force=False) -> tuple:
        li = []
        col = 'Species'
        # find species using 2 chunks
        for c1, c2 in rotate_chunk_pairs(value):
            rows = find(col)(' '.join((c1, c2)), partial=partial, force=force)
            result = cls._instantiate_found(cls, rows, col)
            li.extend(result)
        li = tuple(m for m in li if m)
        return li

    @classmethod
    def nonspecies_progressive_find(cls, value, partial=False, force=False) -> tuple:
        li = []
        col = cls.__name__
        for c in value.split(' '):
            rows = find(col)(c, partial=partial, force=force)
            result = cls._instantiate_found(cls, rows, col)
            li.extend(result)
        li = tuple(m for m in li if m)
        return li

    @classmethod
    def find_specific(cls, value=None, partial=True, first=True, last=False,
                      force=False, progressive: bool = False) -> Union[T, tuple, NoReturn]:
        # col = cls.__name__.lower()
        if progressive:
           if cls == Species:
               return _flexible_return(
                   cls.species_progressive_find(value, partial=partial, force=force),
                   first=first, last=last)
           else:
               return _flexible_return(
                   cls.nonspecies_progressive_find(value, partial=partial, force=force),
                   first=first, last=last)
        else:
            col = cls.__name__
            rows = find(col)(value, partial=partial, force=force)
            result = cls._instantiate_found(cls, rows, col)
            return _flexible_return(result, first=first, last=last)

    @property
    def valid(self):
        try:
            return bool(self.domain)
        except AttributeError:
            return False

    @property
    def taxon(self):
        if self.__class__.__name__ == 'Taxon':
            return None
        return self.__class__.__name__


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
