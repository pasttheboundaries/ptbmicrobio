"""
This package delivers bacterial taxonomy for over 30000 bacterial species

original data come from:
''


Usage note:
Finding bacteria species is only possible for 2 word naming (binomial nomenclature).
Also names must be separated by a single space character, but the case size does not matter.

forms consisting of 3 names or subspecies are not allowed:
Species.find('klebsiella pneumoniae') -> <Species: Klebsiella pneumoniae>
Species.find('klebsiella pneumoniae species') -> None
Species.find('klebsiella pneumoniae ssp. pneumoniae') -> None
"""

import os

LOCAL_PATH = os.path.dirname(__file__)
from .models.interface import find
from .models.taxons import TAXONS, Taxon, Domain, Phylum, Class, Order, Family, Genus, Species, TaxonomicDataFrame
from .common.data import taxonomic_data

__version__ = 1.0
__author__ = 'pasttheboundaries@gmail.com'

# from .experimental.vectorization import OrdinalVectorizer

