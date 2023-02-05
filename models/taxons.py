"""
this module defines basic taxon classes

"""
import pandas as pd
from .interface import find, taxonomic_data
from itertools import chain
from collections import Iterable


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
        if item in self.columns:
            tax = TAXONS[item]
            tax = sorted(list({tax(val) for val in self[item].unique()}), key=lambda x: repr(x))
            first = len(tax) == 1
            return _flexible_return(tax, first)
        return None



class Taxonomy:
    """
    descriptor for Taxon.taxonomy attribute
    Extraxtes rows matching the Taxon instance and wraps them in TaxonomicalDataFrame
    so further taxon of kin can be aextraxted
    like in
    t = Taxon('salmonella')
    tax = t.taxonomy  # type:TaxonomicDataFrame
    tax.genus -> list of related genus or instance of genus
    """
    def __get__(self, instance, owner):
        return self.find_branches(instance)

    @staticmethod
    def find_branches(taxon):
        col = taxon.__class__.__name__.lower()
        rows = taxonomic_data[taxonomic_data[col] == taxon.name]
        return TaxonomicDataFrame(rows)


class Taxon:
    taxonomy = Taxonomy()

    def __init__(self, name):
        self.name = name

    def __getattr__(self, item):
        if item in TAXONS:
            return self.taxonomy.get_taxons(item)
        return self.__getattribute__(item)

    def __hash__(self):
        return hash(str(id(self)))

    def __eq__(self, other):
        if not isinstance(other, Taxon):
            raise TypeError(f'Could not compare Taxon to {type(other)}')
        return repr(self) == repr(other)

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name}>'

    @staticmethod
    def _instantiate_found(cls, df, col):
        if df is None or len(df) == 0:
            return None
        else:
            return tuple(cls(name) for name in df[col])

    @classmethod
    def find(cls, value, strict=False, first=False):
        if cls == Taxon:
            li = [tax.find(value, strict) for tax in TAXONS.values()]
            li = [member for member in li if member]
            return _flexible_return(tuple(chain(*li)), first)
        else:
            col = cls.__name__.lower()
            rows = find(col)(value, strict=strict)
            result = cls._instantiate_found(cls, rows, col)
            return _flexible_return(result, first)

    @property
    def valid(self):
        try:
            return self.domain
        except AttributeError:
            return False


class Domain(Taxon):
    pass


class Phylum(Taxon):
    pass


class Klass(Taxon):
    pass


class Order(Taxon):
    pass


class Family(Taxon):
    pass


class Genus(Taxon):
    pass


class Species(Taxon):
    pass


TAXONS = {t.__name__.lower(): t for t in Taxon.__subclasses__()}
