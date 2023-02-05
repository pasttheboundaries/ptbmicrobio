"""
This package delivers bacterial taxonomy for 17194 bacterial species


Usage note:
Finding bacteria species is only possible for 2 word naming (binomial nomenclature).
Also names must be separated by a single space character, but ase size does not matter.

forms consisting of 3 names or subspecies are not allowed:
Species.find('klebsiella pneumoniae') -> <Species: Klebsiella pneumoniae>
Species.find('klebsiella pneumoniae species') -> None
Species.find('klebsiella pneumoniae ssp. pneumoniae') -> None
"""

import os

LOCAL_PATH = os.path.dirname(__file__)
from .models.interface import find
from .models.taxons import TAXONS, Taxon, Domain, Phylum, Klass, Order, Family, Genus, Species, TaxonomicDataFrame
from .common.data import taxonomic_data
from .extra.vectorization import OrdinalVectoriser

