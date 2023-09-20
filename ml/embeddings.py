"""
this module provides taxonomy tree embedding methods for custom taxon tree embeddings


How it Works:

from ptbmicrobio.ml import TaxonomicEmbeddings
bacteria_list = ['Escherichia coli', 'Klebsiella pneumoniae', 'Staphylococcus aureus']
ndim=16
TE = TaxonomicEmbeddings().embed(bacteria_list, embedding_size=16)
TE.dump('embeddings')

# this saves 2 files :
# - embeddings_V_[timestamp].tsv  - actual embeddings
# - emeddings_M_[timestamp].tsv - metadata (bacteria_list + meta tags)

inne funkcje Embeddings:
 - TaxonomicEmbeddings.load_file(vectors_file) loads both vector files and meta data files, returns self
 - TaxonomicEmbeddings.vectors  # setter, getter #
 - TaxonomicEmbeddings.names  # seter, getter #
 - TaxonomicEmbeddings.ndim - # getter # return embedding dimensions
 - TaxonomicEmbeddings[name]  # __getitem__
"""

import numpy as np
import os
from ptbml.embedding import TreeNodesEmbedding
from ptbmicrobio import load_taxonomic_data
from ptbmicrobio import LOCAL_PATH

DATADIR_PATH = os.path.join(LOCAL_PATH, 'data')


def capitalize_initial(s):
    return ''.join((s[0].upper(), s[1:].lower()))


class FromPretrained:
    available = {'clinical8': ['clinical8_M.tsv', 'clinical8_V.tsv'],
                 'clinical16': ['clinical16_M.tsv', 'clinical16_V.tsv']}

    def __init__(self, TE_instance):
        self.instance = TE_instance

    def __call__(self, arg):
        if arg in self.available:
            paths = [os.path.join(DATADIR_PATH, file) for file in self.available[arg]]
            for path in paths:
                self.instance.load_tsv(path)
        return self.instance


class TaxonomicEmbedding(TreeNodesEmbedding):

    def __init__(self):
        super().__init__()
        self.from_pretrained = FromPretrained(self)

    def embed(self,
              samples,
              embedding_size=8,
              epochs=10,
              batch_size=256,
              intermediate_filename=None,
              from_intermediate=False,
              verbose=1):

        samples = (capitalize_initial(s) for s in samples)
        df = load_taxonomic_data()
        self.df = df.where(np.isin(df.values, samples)).dropna(how='all')
        return super().embed(df=self.df,
                             embedding_size=embedding_size,
                             epochs=epochs,
                             batch_size=batch_size,
                             intermediate_filename=intermediate_filename,
                             from_intermediate=from_intermediate,
                             verbose=verbose)



