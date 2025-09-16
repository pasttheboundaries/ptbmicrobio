import json
from collections.abc import Mapping
from typing import Any, Optional, Callable
from datetime import datetime

# Global registries
SERIALIZABLE_REGISTRY = {}
FOREIGN_SERIALIZABLE_REGISTRY = {}

TYPE_ANNOTATION_KEY = 'TYPE__'
INIT_ANNOTATION_KEY = 'INIT__'
ATTRS_ANNOTATION_KEY = 'ATTRS__'


def register(cls):
    """
    Simple decorator for classes that implement required serialization methods.
    No inheritance needed - just validates interface and registers.
    """
    # Validate required methods exist
    if not hasattr(cls, 'serialization_init_params') or not callable(cls.serialization_init_params):
        raise NotImplementedError(f'{cls.__name__} must implement serialization_init_params() method')

    if not hasattr(cls, 'serialization_instance_attrs') or not callable(cls.serialization_instance_attrs):
        raise NotImplementedError(f'{cls.__name__} must implement serialization_instance_attrs() method')

    # Register the class as-is
    SERIALIZABLE_REGISTRY[cls.__name__] = cls
    return cls


def register_foreign(type_: type,
                     serializable_init_params: Optional[Callable] = None,
                     serialization_instance_attrs: Optional[Callable] = None):
    """Register foreign types for serialization"""
    if not isinstance(type_, type):
        raise TypeError('type_ must be a type')

    if serializable_init_params and not callable(serializable_init_params):
        raise TypeError('serializable_init_params must be callable')

    if serialization_instance_attrs and not callable(serialization_instance_attrs):
        raise TypeError('serialization_instance_attrs must be callable')

    FOREIGN_SERIALIZABLE_REGISTRY[type_.__name__] = {
        TYPE_ANNOTATION_KEY: type_,
        INIT_ANNOTATION_KEY: serializable_init_params,
        ATTRS_ANNOTATION_KEY: serialization_instance_attrs
    }


def is_registered_class(obj):
    """Check if object is from a registered class"""
    return obj.__class__.__name__ in SERIALIZABLE_REGISTRY


def is_foreign_registered(obj):
    """Check if object is from a foreign registered type"""
    return type(obj).__name__ in FOREIGN_SERIALIZABLE_REGISTRY


def ptbs_preprocess(obj):
    """Preprocess objects for serialization"""
    if is_registered_class(obj):
        return {
            TYPE_ANNOTATION_KEY: obj.__class__.__name__,
            INIT_ANNOTATION_KEY: ptbs_preprocess(obj.serialization_init_params()),
            ATTRS_ANNOTATION_KEY: ptbs_preprocess(obj.serialization_instance_attrs())
        }
    elif is_foreign_registered(obj):
        return preprocess_foreign(obj)
    elif isinstance(obj, Mapping):
        return {k: ptbs_preprocess(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [ptbs_preprocess(member) for member in obj]
    else:
        return obj


def preprocess_foreign(obj) -> dict:
    """Handle foreign type preprocessing"""
    registered = FOREIGN_SERIALIZABLE_REGISTRY[type(obj).__name__]

    if init_factory := registered.get(INIT_ANNOTATION_KEY):
        inits = init_factory(obj)
    else:
        inits = None

    if attrs_factory := registered.get(ATTRS_ANNOTATION_KEY):
        attrs = attrs_factory(obj)
        if not isinstance(attrs, dict):
            raise TypeError(f'serialization_instance_attrs must return dict, got {type(attrs)}')
        attrs = {key: ptbs_preprocess(val) for key, val in attrs.items()}
    else:
        attrs = None

    return {
        TYPE_ANNOTATION_KEY: registered[TYPE_ANNOTATION_KEY].__name__,
        INIT_ANNOTATION_KEY: inits,
        ATTRS_ANNOTATION_KEY: attrs
    }


class PtbSerialisationEncoder(json.JSONEncoder):
    def default(self, obj: Any):
        if is_registered_class(obj) or is_foreign_registered(obj):
            return ptbs_preprocess(obj)
        return super().default(obj)


class PtbSerialisationDecoder(json.JSONDecoder):
    def decode(self, obj: str):
        obj = super().decode(obj)
        return self.decode_dispatch(obj)

    def decode_dispatch(self, obj):
        if isinstance(obj, list):
            return [self.decode_dispatch(member) for member in obj]
        elif isinstance(obj, Mapping):
            if TYPE_ANNOTATION_KEY in obj:
                return self.decode_generic(obj)
            return {k: self.decode_dispatch(v) for k, v in obj.items()}
        else:
            return obj

    def decode_generic(self, obj):
        if not isinstance(obj, Mapping):
            raise TypeError('Expected Mapping')

        factory = self.get_factory(obj)
        if not factory:
            return obj

        instance = self.instantiate_serialized(factory, obj[INIT_ANNOTATION_KEY])

        postinit_attrs = obj.get(ATTRS_ANNOTATION_KEY, None)
        if postinit_attrs and isinstance(postinit_attrs, Mapping):
            instance = self.assign_attrs(instance, postinit_attrs)

        try:
            instance._was_serialized = True
        except AttributeError:
            pass

        return instance

    @staticmethod
    def get_factory(obj: Mapping):
        class_name = obj[TYPE_ANNOTATION_KEY]

        # Try registered classes first
        factory = SERIALIZABLE_REGISTRY.get(class_name)
        if factory:
            return factory

        # Try foreign registered types
        foreign_reg = FOREIGN_SERIALIZABLE_REGISTRY.get(class_name)
        if foreign_reg:
            return foreign_reg[TYPE_ANNOTATION_KEY]

        raise ValueError(f'Cannot find factory for {class_name}')

    def instantiate_serialized(self, factory, args):
        args = self.decode_dispatch(args)
        if args:
            if isinstance(args, Mapping):
                unpack_keys = ("*", "**")
                if any(k in args.keys() for k in unpack_keys):
                    unpack_args = args.get("*", tuple())
                    unpack_kwargs = args.get("**", dict())
                    other_kwargs = {k: v for k, v in args.items() if k not in unpack_keys}
                    unpack_kwargs.update(other_kwargs)
                    return factory(*unpack_args, **unpack_kwargs)
                else:
                    return factory(args)
            return factory(args)
        else:
            return factory()

    @staticmethod
    def assign_attrs(instance, postinit_attrs: Mapping):
        for attr, attr_value in postinit_attrs.items():
            setattr(instance, attr, attr_value)
        return instance


def serialize(obj):
    """Serialize objects to JSON string"""
    return json.dumps(ptbs_preprocess(obj), cls=PtbSerialisationEncoder)


def deserialize(obj):
    """Deserialize JSON string to objects"""
    return json.loads(obj, cls=PtbSerialisationDecoder)


class PtbSerializable:
    """Backward compatibility facade"""
    SERIALIZABLE_REGISTRY = SERIALIZABLE_REGISTRY
    FOREIGN_SERIALIZABLE_REGISTRY = FOREIGN_SERIALIZABLE_REGISTRY

    @classmethod
    def register(cls, subclass):
        """Delegate to global register function"""
        return register(subclass)

    @classmethod
    def register_foreign(cls, type_: type, **kwargs):
        """Delegate to global register_foreign function"""
        return register_foreign(type_, **kwargs)


# Register common foreign types
register_foreign(datetime, serializable_init_params=lambda x: {'*': x.timetuple()[:6]})

try:
    from pandas import Timestamp

    register_foreign(Timestamp, serializable_init_params=lambda x: {'*': x.timetuple()[:6]})
except ImportError:
    pass
