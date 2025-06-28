import os
from types import SimpleNamespace
from jinja2 import Template, StrictUndefined, Environment, Undefined, DebugUndefined

def snake_to_pascal(snake_str):
    return ''.join(word.capitalize() for word in snake_str.split('_'))

def expand_string(s: str, context: dict) -> str:
	if not s: return s
	if not isinstance(s, str): return s
	s = os.path.expandvars(s)
	env = Environment(undefined=DebugUndefined)
	template = env.from_string(s)
	try:
		s = template.render(**context)
	except Exception as e:
		# print(f"Error rendering string '{s}' with context {context}: {e}")
		pass
	return s

def expand_dict(config: dict, context: dict):
	## recursively expand environment variables in the config dictionary
	for key, value in config.items():
		if isinstance(value, str):
			config[key] = expand_string(value, context)
		elif isinstance(value, dict):
			expand_dict(value, context)
		elif isinstance(value, list):
			for i in range(len(value)):
				if isinstance(value[i], str):
					value[i] = expand_string(value[i], context)
				elif isinstance(value[i], dict):
					expand_dict(value[i], context)

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
        return (other is None) or (other is _NONE_PROXY)
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