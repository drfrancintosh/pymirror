import os

def snake_to_pascal(snake_str):
    return ''.join(word.capitalize() for word in snake_str.split('_'))

def expand_string(s: str, context: dict) -> str:
	## recursively expand environment variables in the string
	if not s: return s
	if isinstance(s, str):
		s = os.path.expandvars(s)
		s = s.format(**context)
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
