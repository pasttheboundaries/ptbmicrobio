from functools import wraps
import logging
from types import FunctionType


def experimental(obj):
    """
    a decorator to mark deprecated functions or classes
    .
    A warning will be issueed when:
    - the deprecated function is called,
    - or when the deprecated class is instantiated.
    If it is called multiple times it will issue warining only once.
    """
    _called = False

    @wraps(obj)
    def wrapper(*args, **kwargs):
        nonlocal _called
        if not _called:
            logging.warning(f'Function {obj.__name__} ({repr(obj)})  is experimental. '
                            f'It is not validated and might trigger errors or produce false results.')
            _called = True
        return obj(*args, **kwargs)

    def manipulate_class(obj):
        init = obj.__init__

        @wraps(init)
        def false_init(*args, **kwargs):
            nonlocal _called
            if not _called:
                logging.warning(f'Class {obj.__name__} ({repr(obj)}) is experimental. '
                                f'It is not validated and might trigger errors or produce false results.')
                _called = True
            return init(*args, **kwargs)
        obj.__init__ = false_init
        return obj

    if isinstance(obj, FunctionType):
        return wrapper
    elif isinstance(obj, type):
        return manipulate_class(obj)