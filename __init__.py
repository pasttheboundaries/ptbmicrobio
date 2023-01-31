import os

LOCAL_PATH = os.path.dirname(__file__)
from .models.interface import find
from .models.taxons import TAXONS, Taxon, Domain, Phylum, Klass, Order, Family, Genus, Species, TaxonomicDataFrame
from .common.data import bacteria_species
bacteria = bacteria_species

