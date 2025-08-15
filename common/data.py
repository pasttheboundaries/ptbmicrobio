"""
this modlule reads source DataFrame
"""


import os
import pandas as pd
from ptbmicrobio import LOCAL_PATH

TAXONOMIC_DATA_PATH = os.path.join(LOCAL_PATH, 'data', 'bacteria.csv')


def load_taxonomic_data(*names):
    df = pd.read_csv(TAXONOMIC_DATA_PATH)
    if names:
        df = df.loc[df[df.isin(names)].dropna(how='all').index, :].drop_duplicates()
        if len(df) == 0:
            raise ValueError('Declared bacterial names not found')
    return df
