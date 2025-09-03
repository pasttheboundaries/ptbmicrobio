"""
this modlule reads source DataFrame
"""


import os
import pandas as pd

local_path = os.path.dirname(os.path.dirname(__file__))

TAXONOMIC_DATA_PATH = os.path.join(local_path, 'data', 'bacteria.csv')


def load_taxonomic_data(*names):
    df = pd.read_csv(TAXONOMIC_DATA_PATH)
    if names:
        df = df.loc[df[df.isin(names)].dropna(how='all').index, :].drop_duplicates()
        if len(df) == 0:
            raise ValueError('Declared bacterial names not found')
    return df
