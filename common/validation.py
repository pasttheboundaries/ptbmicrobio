import pandas as pd
from typing import Any, Type
from collections.abc import Iterable
from ptbmicrobio.common.errors import ValidationException, MembershipError


def validate_type(obj: Any,
                  *types: Type,
                  parameter_name: str = None,
                  error_message: str = None):

    if parameter_name:
        parameter_name = f'Parameter {parameter_name}'
    else:
        parameter_name = 'Object'

    if not all(isinstance(t, type) for t in types):
        raise TypeError('One of declared types is not type. ')

    if not types:
        raise ValueError('types must be declared')

    if len(types) > 1:
        junction = 'one of'
    else:
        junction = ''

    error_message = error_message or f'{parameter_name} is of wrong type.' \
                                     f' Expected {junction}: {", ".join([t.__name__ for t in types])}'

    if all(not isinstance(obj, t) for t in types):
        raise ValidationException from TypeError(error_message)


def validate_in(obj: Any,
                container: Iterable,
                parameter_name: str = None,
                error_message: str = None):
    if parameter_name:
        parameter_name = f'Parameter {parameter_name}'
    else:
        parameter_name = 'Object'

    if not isinstance(container, Iterable):
        raise TypeError(f'parameter container must be type Iterable to check membership of the obj.')

    error_message = error_message or f'{parameter_name} is not valid.' \
                                     f' Expected objet to one of {container}'

    if not obj in container:
        raise MembershipError(error_message)


def drop_stray_rows(df: pd.DataFrame, drop_condition: callable, subset: Iterable = None, raise_ratio: float = 0.1):
    """
    Drops dataframe rows where condition applied to a cell value is True.

    df: pd.DataFrame
    condition: callable - must be a callable that returns bool type
    subset: IterableIf subset is declared, the condition is checked against the subset columns only.
    raise_ratio: float - decides if the resultant drop dataframe should raise a ValueError or return processed DataFrame

    :return: pd.DataFrame
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f'Expected pandas.DataFrame. Got {type(df)}')
    if len(df) < 1:
        return df

    if subset:
        if any(ss not in df.columns for ss in subset):
            raise ValueError(f'subset argument must be an iterable of df columns names')
        sdf = df[list(subset)]
    else:
        sdf = df

    if not isinstance(drop_condition(sdf.iat[0, 0]), bool):
        raise ValueError(f'drop_condition argument  must be a callable that returns bool type always.')

    bforedrop_len = df.shape[0]
    try:
        df = df[sdf[sdf.map(drop_condition)].isna().all(axis=1)]  # used to be applymap
    except TypeError as e:
        raise TypeError(f'drop_condition callable is not suitable for the data.') from e
    afterdrop_len = df.shape[0]
    if (bforedrop_len - afterdrop_len) / bforedrop_len > raise_ratio:
        raise ValueError(
            f'Too many stray rows in \n{df.head(5)}\n.\n.\n.\nshape={df.shape}\nAcceptable ratio is set to {raise_ratio}, but found more.')
    return df