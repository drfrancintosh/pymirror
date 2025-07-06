from dataclasses import dataclass
import os
from time import time
import requests
import json

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

    def get_text(self, params=None):
        if self.cache_file:
            result = self._fetch_from_cache()
            if result: return result
        
        # If no cache or cache failed, fetch from URL
        response = requests.get(self.url, params=params if params else None)
        if response.ok:
            self._save_to_cache(response.text)
            result = response.text
        else:
            print(f"Error fetching data: {response.status_code} - {response.text}")
            result = {"error": "error"}
        return result

    def get_json(self, params=None):
        text = self.get_text(params)
        if text:
            result = json.loads(text)
        else:
            result = {"error": "error"}
        return result
