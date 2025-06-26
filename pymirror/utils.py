import os
from types import SimpleNamespace
from jinja2 import Template

def snake_to_pascal(snake_str):
    return ''.join(word.capitalize() for word in snake_str.split('_'))

def expand_string(s: str, context: dict) -> str:
	## recursively expand environment variables in the string
	if not s: return s
	if isinstance(s, str):
		s = os.path.expandvars(s)
		try:
			template = Template(s)
			s = template.render(**context)
		except Exception as e:
			## print(f"KeyError: {e} in string '{s}' with context {context}")
			pass
	return s

def expand_dict(config: dict, context: dict):
	## recursively expand environment variables in the config dictionary
	for key, value in config.items():
		if isinstance(value, str):
			print(f"Expanding {key} = {value}, {context}")
			config[key] = expand_string(value, context)
		elif isinstance(value, dict):
			expand_dict(value, context)
		elif isinstance(value, list):
			for i in range(len(value)):
				if isinstance(value[i], str):
					value[i] = expand_string(value[i], context)
				elif isinstance(value[i], dict):
					expand_dict(value[i], context)

class SafeNamespace(SimpleNamespace):
    def __init__(self, **kwargs):
        # Recursively convert dicts and lists to SafeNamespace
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
        # Override __getattr__ to return None for undefined attributes
        return None

    def __getitem__(self, name):
        # Implement __getitem__ to allow [] notation
        return getattr(self, name, None)
