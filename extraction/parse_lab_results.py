from typing import Union, List, Dict, Tuple
import re
from itertools import zip_longest

import pandas as pd
from .constants import *
from ..common.validation import drop_stray_rows
from ..common.native_types import ParsedData, ParsedCulture, ParsedCultureResult, SensitivityReadout, AST
from ptbabx import antibiotic
from .constants import ResistanceTags as tags


def is_culture(wynik: str) -> bool:
    """
    auxilliary function for a quickcheck
    """
    return bool(re.search(CULTURE_PARSE_SAMPLE_RE, wynik))


def parse_resistance_string(rs: str) -> str:
    rs = rs.lower()
    if rs in 'or':
        return tags.RESISTANT
    elif rs in 'sw':
        return tags.SENSITIVE
    elif rs in 'imp':
        return tags.INTERMEDIATE
    else:
        return tags.UNKNOWN


def culture_header(wynik):
    header = {
        'sample': re.search(CULTURE_PARSE_SAMPLE_RE, wynik),
        'description': re.search(CULTURE_PARSE_DESCR_RE, wynik),
        'date': re.search(CULTURE_PARSE_DATE_RE, wynik),
        'notes': re.search(CULTURE_PARSE_NOTE_RE, wynik)
    }
    return ParsedCulture({k: v.groups()[0].strip() for k, v in header.items() if v})


def parse_abx(abx: str) -> Tuple[str, SensitivityReadout]:
    return antibiotic(abx[1]).name, SensitivityReadout(parse_resistance_string(abx[2]), abx[4])


def parse_antibiogram(antibiogram) -> AST:
    abxs: List[str] = re.findall(CULTURE_PARSE_RESISTANCE_RE, antibiogram)
    return AST(tuple(parse_abx(abx)) for abx in abxs)


def parse_culture(wynik: str) -> Union[List[Dict], None]:
    """
    Parses a string culture result from WSSK hospital
    :param wynik: str - original input data
    :return: built-in structures

    Comment:
    Multiple pathogens are reported in one result - hence the output is list.

    Single pathogen culture readout is stored in a dictionary
        Keys of the dictionary are:
            sample  (for sample site)
            description (lab parsed description)
            pathogen (microorganism name)
            notes (further lab notes)
            ast (antibiotic sensitivity testing)

    """

    parsed = ParsedCultureResult()
    header = culture_header(wynik)  # parsed
    pathogens: list = re.findall(CULTURE_PARSE_PATOGEN_RE, wynik)
    asts: list = [parse_antibiogram(abg[0]) for abg in re.findall(CULTURE_PARSE_ABGRAM_RE, wynik)]

    if header and not pathogens:  # lab note deteced, no pathogen detected
        parsed.append(header)

    elif header and pathogens:  # pathogen detected
        # a loop appending to the ouput list for multiple pathogens reported
        for pathogen, ast in zip_longest(pathogens, asts, fillvalue=''):
            result = ParsedCulture(header)
            result.update({'pathogen': pathogen, 'ast': ast})
            parsed.append(result)
    else:  # unknown circumstances - exception must be reised
        raise NotImplementedError(f'Parsed found an unusual pattern.\n {wynik}')

    if not parsed:
        return None  # if parser unable to parse and Exception not reised
    else:
        return parsed



def parse_dataframe(df: pd.DataFrame, column: Union[str, int], raise_ratio=0.01) -> pd.DataFrame:
    # this is actually a validation functionality but won't raise if invalid rows are less than raise_ratio
    pre_l = len(df[column])
    df = drop_stray_rows(df,
                         drop_condition=lambda x: not is_culture,
                         subset=[column],
                         raise_ratio=raise_ratio)

    df[column] = df[column].apply(parse_culture)

    not_parsed = 0
    for item in df[column]:
        if not isinstance(item, ParsedData):
            not_parsed += 1
    l = len(df[column])
    print(f'Attempted parsing {pre_l}, excluded={pre_l-l}, success={l-not_parsed}, failed={not_parsed}')
    return df


