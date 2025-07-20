import os
from types import SimpleNamespace
from jinja2 import Template, StrictUndefined, Environment, Undefined, DebugUndefined

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
		# print(f"Error rendering string '{s}' with context {context}: {e}")
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

def color_to_tuple(x):
    if x == None: return (0, 0, 0)  # default to black if None
    r = (x >> 19) & 0x1F
    g1 = (x >> 16) & 0x07
    g0 = (x >> 5) & 0x07
    b = x & 0x1F
    rgb = (r/31.0, (g1 << 3 | g0) / 63.0, b/31.0)
    return rgb

def color_from_tuple(rgb):
    ### convert RGB tuple to HTML #rrggbb format
    return f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"

def fromcolor(t) -> str:
    """Convert a color integer to an RGB hex string."""
    if t is None:
        return None
    if isinstance(t, str):
        return t  # Already a string
    if not isinstance(t, int):
        raise ValueError(f"Invalid color format {t}, expected integer.")
    r = (t >> 19) & 0x1F
    g1 = (t >> 16) & 0x07
    g0 = (t >> 5) & 0x07
    b = t & 0x1F
    r = r << 3
    g = (g1 << 3 | g0) << 2
    b = b << 3
    result = f"#{r:02x}{g:02x}{b:02x}"
    return result

def tocolor(t) -> int:
    if t == None:
        return None
    if isinstance(t, int):
        return t  # Already an integer
    if not isinstance(t, str):
        raise ValueError(f"Invalid color format {t}, expected RGB hex string.")
    if t.startswith("#"):
        t = t.lstrip("#")
    if len(t) == 3:
        t = tuple(int(t[i] * 16, 16) for i in (0, 1, 2))
    elif len(t) == 6:
        t = tuple(int(t[i : i + 2], 16) for i in (0, 2, 4))
    else:
        raise ValueError(f"Invalid hex color format '{t}', expected 3 or 6 hex digits.")
    r, g, b = t
    r = (r >> 3) & 0x1F  # Convert to 5 bits
    g0 = (g >> 2) & 0x07  # Convert to lower 3 bits
    g1 = (g >> 5) & 0x07  # Convert to upper 3 bits
    b = (b >> 3) & 0x1F  # Convert to 5 bits
    x = r << 19 | (g1 << 16 | g0 << 5 | b)
    return x

def getter(obj, path, default=None):
    keys = path.split(".")
    current = obj
    for key in keys:
        print(f"Accessing key: {key} in {current}")
        if isinstance(current, dict):
            current = current.get(key, default)
        elif isinstance(current, list):
            current = current[int(key)]
        else:
            return default
    return current
