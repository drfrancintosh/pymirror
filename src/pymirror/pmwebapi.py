from dataclasses import dataclass
import os
import time
import requests
import json
from .pmlogger import _debug, _print, _error

@dataclass
class PMWebApi:
    url: str
    cache_file: str = None
    cache_timeout: int = 3600  # Default cache timeout in seconds

    def _fetch_from_cache(self):
        if  not os.path.exists(self.cache_file):
            return None
        if os.path.getsize(self.cache_file) == 0:
            return None
        # get files stats and check if it is older cache_timeout ago
        if not self.cache_timeout or self.cache_timeout <= 0:
            return None
        # get files stats and check if it is older cache_timeout from current time
        file_age = os.path.getmtime(self.cache_file)
        if (file_age + self.cache_timeout) < time.time():
            return None  # Cache is too old, do not use it
        # Read the cached file
        with open(self.cache_file, 'r') as file:
            text = file.read()
        return text

    def _save_to_cache(self, text):
        if not self.cache_file:
            return
        # Ensure the directory exists
        # os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        # Write the text to the cache file
        with open(self.cache_file, 'w') as file:
            file.write(text)

    def get_text(self, _params=None):
        if self.cache_file:
            result = self._fetch_from_cache()
            if result: return result
        
        # If no cache or cache failed, fetch from URL
        params = _params.copy() if _params else {}
        now = time.time()
        url = self.url
        if "_resource_id" in params:
            url = f"{self.url}/{params['_resource_id']}"
            del params["_resource_id"]
        _debug(f"{now}: Fetching data from {url} with params: {params}")
        response = requests.get(url, params=params)
        if response.ok:
            self._save_to_cache(response.text)
            result = response.text
        else:
            _error(f"Error fetching data: {response.status_code} - {response.text}")
            result = None
        return result

    def get_json(self, params=None):
        text = self.get_text(params)
        _debug(f"Response text: {text}")
        if text:
            result = json.loads(text)
        else:
            result = None
        return result
