"""
This package delivers bacterial taxonomy for over 30000 bacterial species

original pairs_generator come from:
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
from .models.taxons import Taxon, Species, Genus, Phylum, Order, Class, Domain, TAXONS, Family
from .common.native_types import AST, ParsedData, ParsedDataFrame,ParsedCulture, ParsedCultureResult, SensitivityReadout

LOCAL_PATH = os.path.dirname(__file__)

__version__ = "0.1.1"
__author__ = 'pasttheboundaries@gmail.com'

# from .experimental.vectorization import OrdinalVectorizer

