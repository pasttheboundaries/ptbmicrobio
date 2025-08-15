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
import ptbtree
import logging
from ptbml.embedding import TreeNodeEmbedding, TreeNodePairs
from ptbmicrobio import load_taxonomic_data
from ptbmicrobio import LOCAL_PATH


DATADIR_PATH = os.path.join(LOCAL_PATH, 'data')


logger = logging.getLogger('PTB')


def capitalize_initial(s):
    return ''.join((s[0].upper(), s[1:].lower()))

def construct_weights_array(df):
    df_width = df.shape[1]
    df_length = df.shape[0]
    # return np.arange(df_width - 1, 0, -1) * np.ones((df_length, df_width - 1)).astype(np.float32)
    return [6, 5, 4, 3, 2, 1]
    # return 1

PRETRAINED = {'clinical8': ['clinical8_M.tsv', 'clinical8_V.tsv'],
              'clinical16': ['clinical16_M.tsv', 'clinical16_V.tsv']}

class TaxonomicEmbedding(TreeNodeEmbedding):

    def __init__(self):
        super().__init__()

    @classmethod
    def from_pretrained(cls, pretrained):
        if pretrained in PRETRAINED:
            paths = [os.path.join(DATADIR_PATH, file) for file in PRETRAINED[pretrained]]
            instance = cls()
            for path in paths:
                instance.load_tsv(path)
        return instance

    # noinspection PyMethodOverriding
    def embed(self,
              samples = None,
              embedding_size=8,
              intermediate_dirname=None,
              training_setup=None,
              verbose=1):

        """
        :param samples: a collection of bacterial names
        :param epochs: int, default = 10
        :param batch_size: int, default = 256
        :param intermediate_filename: If not given
        :param verbose:
        :return:
        """
        logger.info('TaxonomicEmbedding.embed called')
        if (not samples) and (not intermediate_dirname):
            raise ValueError('''TaxonomicEmbeddings embedding requires samples [list of bacterial names ] 
            or intermediate dirname must be given.''')

        if samples:
            samples = np.array([capitalize_initial(s) for s in samples])
            df = load_taxonomic_data(*samples)
            tree = ptbtree.Tree.from_df(df, weights=construct_weights_array(df))
        elif intermediate_dirname:
            tree = TreeNodePairs.from_saved(intermediate_dirname)
        else:
            raise ValueError(f'TaxonomicEmbedding.embed requires eiter a list of bacreial names or a directory path to the sotred TreeNodePairs')
        return super().embed(tree=tree,
                             embedding_size=embedding_size,
                             intermediate_dirname=intermediate_dirname,
                             setup=training_setup,
                             verbose=verbose)



