"""
this modlule reads source DataFrame
"""


import os
import pandas as pd
from ptbmicrobio import LOCAL_PATH

TAXONOMIC_DATA_PATH = os.path.join(LOCAL_PATH, 'data', 'bacteria.csv')

taxonomic_data = pd.read_csv(TAXONOMIC_DATA_PATH)


