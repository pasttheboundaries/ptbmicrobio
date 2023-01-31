"""
this modlule reads source DataFrame
"""


import os
import pandas as pd
from ptbmicrobio import LOCAL_PATH


bacteria_path = os.path.join(LOCAL_PATH, 'data', 'bacteria.csv')

bacteria_species = pd.read_csv(bacteria_path)
