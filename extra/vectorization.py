"""
OrdinalVectoriser
provides means to vectorise ptbmicrobio taxons
This is achieved be applying enumeration to sorted taxonomy_data table
By this means the vectors up to Genus of one taxon group will be located close to each other in the vectorspace.
The taxon groups above will be located at the mean values.
This is deceptive as the correlation and vector proximity in that case will be in the middle of ordinal space.
For example
vector for Genus : staphylococcus will be closest to Staphylococcus hominis
which has no particular meanin
apart from Staphylococcus agnetis beining in the middle of ordinal (alphabetical) values for staphylococcus species.

In this respect OrdinalVectoriser produces naive vectors distributed in ordinal vector space.
This means proximity of vectors has no other meaning than just alphabetical proximity.

"""

from hisforsee.common.validation import validate_type
from ptbmicrobio import taxonomic_data, Taxon
from ptbmicrobio.models.ast import Sensitivity
import pandas as pd
from cantibiotics import GROUPS
from itertools import chain

import numpy as np


def enumerate_df_categoricals(df, normalized=True):
    categorical_columns = [col for col in df.columns if isinstance(df[col].dtype, pd.CategoricalDtype)]
    for col in categorical_columns:
        if col == 'species':
            en = dict((v, k) for k, v in enumerate(list(df[col])))
        else:
            en = dict((v, k) for k, v in enumerate(list(pd.Categorical(df[col]).categories)))
        if normalized:
            maks = max(tuple(en.values()))
            en = {k: v/maks for k,v in en.items()}
        df[col] = df[col].map(en).astype(float)
    return df


class OrdinalVectoriser:
    VALID_TYPE = Taxon

    def __init__(self, normalised=True):
        self.normalised = normalised
        self.vectorised_data = enumerate_df_categoricals(taxonomic_data.copy().astype('category'),
                                                         normalized=normalised)

    def vectorise(self, taxon):
        validate_type(taxon, self.VALID_TYPE, parameter_name='taxon',
                      error_message=f'OrdinalVectoriser can only vectorise {self.VALID_TYPE}.'
                                    f' Got type {type(taxon)}')
        taxonomy_df = taxon.taxonomy
        inds = list(taxonomy_df.index)
        vectorised_df = self.vectorised_data.loc[inds, :]
        col_means = vectorised_df.mean(axis=0)
        print(vectorised_df)
        print(col_means)

        ind = vectorised_df.index[0]

        # to numpy.ndarray
        vectorised = self.vectorised_data.loc[ind, :].values

        # ascribing means
        """
        in case of lower taxons, the higher taxon value is a mean of all upper values
        like in 
        Genus values vor domain , klass, order, familu and genus will be taber values
        but for Species it will be mean of all species tabelar values,
        to assure the species dimension vector is localised where the mean is for the group (genus).
        
        """
        col = taxon.__class__.__name__.lower()
        col_n = tuple(taxonomic_data.columns).index(col)
        vectorised[col_n + 1:] = col_means[col_n + 1:]
        return vectorised

    def __call__(self, taxon):
        return self.vectorise(taxon)


class ASLVectoriser:
    def __init__(self):
        pass

    @staticmethod
    def _deliver_by_antibiotic(antibiotic_sensitivity_list):
        """
        delivers vector of size = len(ANTIBIOTICS) # all available antibiotics
        """
        unk = Sensitivity('u').numeric
        grouped_abxs = tuple(chain(*[group.list for group in GROUPS]))  # abxs grouped by typde
        senses = {abx.name: unk for abx in grouped_abxs}  # all = -1
        # update accordingly
        senses.update({asens.antibiotic.name: asens.sensitivity.numeric for asens in antibiotic_sensitivity_list})
        return np.array(tuple(senses.values()))

    @staticmethod
    def _deliver_by_group(antibiotic_sensitivity_list):
        """
        delivers vector of size = len(GROUPS) # all available antibiotic groups
        """
        unk = Sensitivity('u').numeric
        senses = {group.name: unk for group in GROUPS}  # all groups = -1
        grouped_asensitivities = dict()
        for asens in antibiotic_sensitivity_list:
            group = asens.antibiotic.group
            group_list = grouped_asensitivities.get(group, list())
            group_list.append(asens.sensitivity.numeric)
            grouped_asensitivities[group] = group_list
        grouped_asensitivities = {k : sum(v)/len(v) for k,v in grouped_asensitivities.items()}
        senses.update(grouped_asensitivities)  # update accordingly
        return np.array(tuple(senses.values()))

    def vectorise(self, antibiotic_sensitivity_list, grouped=False):
        if grouped:
            return self._deliver_by_group(antibiotic_sensitivity_list)
        else:
            return self._deliver_by_antibiotic(antibiotic_sensitivity_list)


    def __call__(self, antibiotic_sensitivity_list, grouped=True):
        return self.vectorise(antibiotic_sensitivity_list, grouped=grouped)
