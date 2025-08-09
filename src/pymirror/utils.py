import datetime
import os
from types import SimpleNamespace
from jinja2 import Template, StrictUndefined, Environment, Undefined, DebugUndefined
from .pmlogger import _debug
from dataclasses import fields
from typing import Dict, Any

def snake_to_pascal(snake_str):
    return ''.join(word.capitalize() for word in snake_str.split('_'))

def expand_string(s: str, context: dict, dflt: str = None) -> str:
	if not s: return s
	if not isinstance(s, str): return s
	s = os.path.expandvars(s)
	env = Environment(undefined=DebugUndefined)
	template = env.from_string(s)
	try:
		s = template.render(**context)
	except Exception as e:
		# _debug(f"Error rendering string '{s}' with context {context}: {e}")
		return dflt if dflt is not None else s
	return s

def expand_dict(config: dict, context: dict, dflt: str = None):
	## recursively expand environment variables in the config dictionary
	for key, value in config.items():
		if isinstance(value, str):
			config[key] = expand_string(value, context, dflt)
		elif isinstance(value, dict):
			expand_dict(value, context, dflt)
		elif isinstance(value, list):
			for i in range(len(value)):
				if isinstance(value[i], str):
					value[i] = expand_string(value[i], context, dflt)
				elif isinstance(value[i], dict):
					expand_dict(value[i], context, dflt)

##
## This is a proxy class that returns None for any attribute or item access.
## It is used to safely handle missing attributes in SafeNamespace.
##
class _NoneProxy:
    def __getattr__(self, name):
        return _NONE_PROXY
    def __getitem__(self, name):
        return _NONE_PROXY
    def __eq__(self, other):
        return (other == None)
    def __bool__(self):
        return False
    def __repr__(self):
        return "None"

_NONE_PROXY = _NoneProxy()

## This is a safe namespace class that returns None for any missing attributes.
class SafeNamespace(SimpleNamespace):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if isinstance(v, dict):
                kwargs[k] = SafeNamespace(**v)
            elif isinstance(v, list):
                kwargs[k] = [
                    SafeNamespace(**i) if isinstance(i, dict) else i for i in v
                ]
        super().__init__(**kwargs)
        self.__dict__.update(kwargs)

    def __getattr__(self, name):
        # Return _NONE_PROXY for missing attributes
        return _NONE_PROXY

    def __getitem__(self, name):
        return getattr(self, name, _NONE_PROXY)

def _add(t, d):
	"""Increment each element of the tuple by the corresponding element in d."""
	return tuple(a + b for a, b in zip(t, d))

def _sub(t1, t2):
	"""Calculate the difference between two tuples."""
	return tuple(a - b for a, b in zip(t1, t2))

def _scale(t1, s):
	return tuple(x * s for x in t1)

def _div(t1, t2):
	return tuple(x / y for x, y in zip(t1, t2))

def _mul(t1, t2):
	return tuple(x * y for x, y in zip(t1, t2))

def _norm(t1):
	## take the norm of the tuple
	return sum(x * x for x in t1) ** 0.5

def _height(rect: tuple) -> int:
    return rect[3] - rect[1]

def _width(rect: tuple) -> int:
    return rect[2] - rect[0]

def _str_to_rect(rect: str) -> tuple:
    """Convert a rectangle string to a tuple of floats."""
    if not rect:
        return (0.0, 0.0, 1.0, 1.0)
    try:
        return tuple(float(x) for x in rect.split(','))
    except ValueError as e:
        raise ValueError(f"Invalid rectangle format: {rect}") from e

def getter(obj, path, default=None):
    keys = path.split(".")
    current = obj
    for key in keys:
        _debug(f"Accessing key: {key} in {current}")
        if isinstance(current, dict):
            current = current.get(key, default)
        elif isinstance(current, list):
            current = current[int(key)]
        else:
            return default
    return current

def from_dict(cls):
    """Decorator to add from_dict class method to any dataclass"""
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]):
        """Create instance from dict, ignoring extra keys"""
        valid_fields = {f.name for f in fields(cls)}
        filtered_dict = {k: v for k, v in config_dict.items() if k in valid_fields}
        return cls(**filtered_dict)
    
    cls.from_dict = from_dict
    return cls

def to_int(s: str, dflt: int = 0) -> int:
    try:
        return int(s)
    except ValueError:
        return dflt