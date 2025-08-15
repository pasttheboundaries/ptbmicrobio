"""
this module provides rules to identify alert patogens according to :
DZ.UST. RP. Poz. 240 OBWIECZENIE MINISTRA ZDROWIA z dnia 22 stycznia 2021 r.

1) gronkowiec złocisty (Staphylococcus aureus) oporny na metycylinę (MRSA) lub glikopeptydy (VISA lub VRSA) lub
oksazolidynony;
2) enterokoki (Enterococcus spp.) oporne na glikopeptydy (VRE) lub oksazolidynony;
3) pałeczki Gram-ujemne Enterobacteriaceae spp. wytwarzające beta-laktamazy o  rozszerzonym spektrum substratowym (np. ESBL, AMPc, KPC) lub oporne na karbapenemy lub inne dwie grupy leków lub polimyksyny;
4) pałeczka ropy błękitnej (Pseudomonas aeruginosa) oporna na karbapenemy lub inne dwie grupy leków lub polimyksyny;
5) pałeczki niefermentujące Acinetobacter spp. oporne na karbapenemy lub inne dwie grupy leków lub polimyksyny;
6) szczepy chorobotwórcze laseczki beztlenowej Clostridium difficile oraz wytwarzane przez nie toksyny A i B;
7) laseczka beztlenowa Clostridium perfringens;
8) dwoinka zapalenia płuc (Streptococcus pneumoniae) oporna na cefalosporyny III generacji lub penicylinę;
9) grzyby Candida oporne na flukonazol lub inne leki z grupy azoli lub kandyn;
10) grzyby Aspergillus;
11) rotawirus (rotavirus);
12) norowirus (norovirus);
13) wirus syncytialny (respiratory syncytial virus);
14) wirus zapalenia wątroby typu B;
15) wirus zapalenia wątroby typu C;
16) wirus nabytego niedoboru odporności u ludzi (HIV);
17) biologiczne czynniki chorobotwórcze izolowane z krwi lub płynu mózgowo-rdzeniowego, odpowiedzialne za uogólnione lub inwazyjne zakażenia.
"""

import pandas as pd
from typing import Optional, Union
from ..models.taxons import Taxon
from ..common.native_types import AST, ParsedCultureResult, ParsedDataFrame
from ptbabx import antibiotic
from .constants import RESISTANT
from functools import lru_cache
import multiprocessing


METHICILLIN = antibiotic('metycylina')
VANCOMYCIN = antibiotic('wankomycyna')
LINEZOLID = antibiotic('linezolid')
KARBAPENEMS = antibiotic('meropenem').group
COLISTIN = antibiotic('kolistyna')
CEPHALOSPORINS3 = antibiotic('ceftazydym').group


@lru_cache(maxsize=200)
def taxon_find(patogen_name):  # this is a proxy for memoisation purposes
    tax =  Taxon.find(patogen_name, first=True)
    if not tax:
        tax = Taxon.find(patogen_name, first=True, progressive=True)
    return tax


def match_taxon(patogen_name: str, taxon_tier_name: str, taxon_name_match: str) -> bool:
    """
    :param patogen_name: name to be verified
    :param taxon_tier_name: Species, Genus or Family
    :param taxon_name_match: name of the matching taxon
    :return: bool
    """
    taxon = getattr(taxon_find(patogen_name), taxon_tier_name, None)
    if not taxon:
        return False
    elif isinstance(taxon, tuple):  # not matching taxon tiers
        return False
    elif taxon.__class__.__name__ == taxon_tier_name:
        if taxon.name.lower() == taxon_name_match.lower():
            return True
        else:
            return False
    else:
        return False


def match_antibiotic_resistant(ast, *key_antibiotics):
    """
    cheks if there is resistance in ast against one of the key_antibiotics
    :param ast:
    :param key_antibiotics:
    :return:
    """
    if any(antibiotic(k).name in key_antibiotics and v.resistance == RESISTANT for k, v in ast.items()):
        return True
    return False


def match_antibiotic_group_resistant(ast, antibiotic_group_name: str):
    """
    checks if there is a resistance against a certain group of antibiotics in ast
    :param ast:
    :param antibiotic_group_name:
    :return:
    """
    if any(antibiotic(k).group == antibiotic_group_name and v.resistance == RESISTANT for k, v in ast.items()):
        return True
    return False


def rule1(patogen_name: str, ast: AST, notes: Optional[str] = None):
    """
    rule1 refers to:
    1) gronkowiec złocisty (Staphylococcus aureus) oporny na metycylinę (MRSA) lub glikopeptydy (VISA lub VRSA) lub
        oksazolidynony
    :param patogen_name: str - name of patogen to be checked
    :param ast: AST (parsed ast, ParsedData subclass instance)
    :param notes:
    :return:
    """
    if not match_taxon(patogen_name, 'Species', 'Staphylococcus aureus'):
        return False
    if notes and any(val in notes.lower() for val in ('mrsa', 'visa', 'vrsa')):
        return True
    if match_antibiotic_resistant(ast, METHICILLIN.name, VANCOMYCIN.name, LINEZOLID.name):
        return True
    return False


def rule2(patogen_name: str, ast: AST, notes: Optional[str] = None):
    """
    rule2 refers to:
        2) enterokoki (Enterococcus spp.) oporne na glikopeptydy (VRE) lub oksazolidynony;
    :param patogen_name: str - name of patogen to be checked
    :param ast: AST (parsed ast, ParsedData subclass instance)
    :param notes:
    :return:
        """
    if not match_taxon(patogen_name, 'Genus', 'Enterococcus'):
        return False
    if notes and 'vre' in notes.lower():
        return True
    if match_antibiotic_resistant(ast, VANCOMYCIN.name, LINEZOLID.name):
        return True
    return False


def rule345(patogen_name: str, ast: AST, notes: Optional[str] = None):
    """
    rule345 refers to:
        3) pałeczki Gram-ujemne Enterobacteriaceae spp. wytwarzające beta-laktamazy
         o  rozszerzonym spektrum substratowym (np. ESBL, AMPc, KPC)
          lub oporne na karbapenemy
          lub inne dwie grupy leków
          lub polimyksyny;
          AND
        4) pałeczka ropy błękitnej (Pseudomonas aeruginosa)
        oporna na karbapenemy
        lub inne dwie grupy leków
        lub polimyksyny;
          AND
        5) pałeczki niefermentujące Acinetobacter spp.
        oporne na karbapenemy
        lub inne dwie grupy
        leków lub polimyksyny;

    :param patogen_name: str - name of patogen to be checked
    :param ast: AST (parsed ast, ParsedData subclass instance)
    :param notes:
    :return:
    """
    if not (
            match_taxon(patogen_name, 'Family', 'Enterobacteriaceae')
            and
            match_taxon(patogen_name, 'Species', 'Pseudomona aeruginosa')
            and
            not match_taxon(patogen_name, 'Genus', 'Acinetobacter')
    ):
        return False
    if notes and any(val in notes.lower() for val in ('esbl', 'ampc', 'kpc')):
        return True
    if match_antibiotic_resistant(ast, COLISTIN.name):
        return True
    if match_antibiotic_group_resistant(ast, KARBAPENEMS):
        return True
    resistant_groups = {antibiotic(k).group for k, v in ast.items() if v.resistance == RESISTANT}
    if len(resistant_groups) >= 2:
        return True
    return False


def rule67(patogen_name: str, *args):
    """
    rule67 refers to
    6) szczepy chorobotwórcze laseczki beztlenowej Clostridium difficile oraz wytwarzane przez nie toksyny A i B;
    AND
    7) laseczka beztlenowa Clostridium perfringens;
    :param patogen_name: str - name of patogen to be checked
    :param ast: AST (parsed ast, ParsedData subclass instance)
    :param notes:
    :return:
     """
    if (
            match_taxon(patogen_name, 'Species', 'Clostridium difficile')
            or
            match_taxon(patogen_name, 'Species', 'Clostridium perfringens')
    ):
        return True
    return False


def rule8(patogen_name: str, ast: AST, notes: Optional[str] = None):
    """
    rule8 refers to
    8) dwoinka zapalenia płuc (Streptococcus pneumoniae) oporna na cefalosporyny III generacji lub penicylinę;
    :param patogen_name: str - name of patogen to be checked
    :param ast: AST (parsed ast, ParsedData subclass instance)
    :param notes:
    :return:
     """
    if not match_taxon(patogen_name, 'Species', 'Streptococcus pneumoniae'):
        return False
    if match_antibiotic_group_resistant(ast, CEPHALOSPORINS3):
        return True
    return False


ALERT_RULES = (rule1, rule2, rule345, rule67, rule8)


def is_alert_patogen(patogen_name: str, ast: AST):
    return any(rule(patogen_name, ast) for rule in ALERT_RULES)


def alert_patogen_rules(culture_result: ParsedCultureResult) -> bool:
    """
    this function is to be applied to parsed content column of cultures stored in adb
    :param culture_result:
    :return:
    """
    for culture in culture_result:
        if (patogen := culture.get('patogen', None)) and (ast := culture.get('ast', None)):
            if is_alert_patogen(patogen, ast):
                return True
    return False


def extract_alert_column(df: pd.DataFrame, column: Union[str, int], alert_column_name='alert') -> pd.DataFrame:
    """
    creates alert column in the df in preprocessing pipeline
    This column will contain bool type
    """

    values = df[column]
    with multiprocessing.Pool(processes=4) as pool:
        df[alert_column_name] = pool.map(alert_patogen_rules, values)
    return df
