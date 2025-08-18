from dataclasses import dataclass
import os
import time
from unittest import result
from urllib import response
from wsgiref import headers
import httpx
import asyncio
import json

import requests
from .pmlogger import _debug, _print, _error

class PMWebApi:
    def __init__(self, url: str, cache_file: str = None, cache_timeout: int = 3600):
        self.url = url
        self.cache_file = cache_file
        self.cache_timeout = cache_timeout  # Default cache timeout in seconds
        self.next_timeout = 0
        self.cache_text = None
        self.method = "get"  # Default method
        self.headers = {"Accept": "application/json"}
        self.params = {}
        self.data = None
        self.json = None
        self.loop = None
        self.task = None

    def _get_fresh_cache_filename(self):
        if (
           not self.cache_file
           or not os.path.exists(self.cache_file)
           or os.path.getsize(self.cache_file) == 0
           or self.cache_timeout <= 0):
            #if there's no cache file, return None
            return None
        file_age = os.path.getmtime(self.cache_file)
        if (file_age + self.cache_timeout) < time.time():
            return None  # Cache is too old, do not use it
        return self.cache_file

    def _fetch_from_file_cache(self):
        # get files stats and check if it is older cache_timeout from current time
        # Read the cached file
        cache_file = self._get_fresh_cache_filename()
        if not cache_file:
            return None
        with open(cache_file, 'r') as file:
            text = file.read()
        return text

        pass

    def _fetch_from_cache(self):
        if self.next_timeout > time.time():
            # if not timed out, return last cache
            if self.cache_text:
                ## if we have local cache, return it
                return self.cache_text
            else:
                ## otherwise try to get it from the cache_file
                return self._fetch_from_file_cache()
        else:
            # if timed out, reset cache
            self.cache_text = None
            return None

    def _save_to_cache(self, text):
        self.cache_text = text
        self.next_timeout = time.time() + self.cache_timeout
        if not self.cache_file:
            return
        # Ensure the directory exists
        # os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        # Write the text to the cache file
        with open(self.cache_file, 'w') as file:
            file.write(text)

    async def _fetch(self):
        async with httpx.AsyncClient() as client:
            method = self.method.upper()
            print(f"Fetching {self.url} with method {method}...")
            # Select the method dynamically
            response = await client.request(
                method,
                self.url,
                headers=self.headers,
                params=self.params,
                data=self.data if method != "GET" else None,
                json=self.json if method != "GET" else None,
                follow_redirects=True
            )
            print(f"Received response from {self.url} with status code {response.status_code}")
            return response

    def start(self): 
        self.loop = asyncio.get_event_loop()
        self.task = self.loop.create_task(self._fetch())

    def cancel(self):
        if self.task:
            self.task.cancel()
            self.task = None

    def fetch(self, blocking=True):
        try:
            if blocking:
                self.loop.run_until_complete(self.task)
            else:
                ## give asyncio some time to process
                self.loop.run_until_complete(asyncio.sleep(0.001))
            if self.task.done():
                result = self.task.result()
                return result
            return None
        except Exception as e:
            response = {
                "status_code": 500,
                "text": str(e),
                "headers": {},
                "reason": "PyMirror Exception"
            }
            return response

    def fetch_text(self, blocking=True):
        cache = self._fetch_from_cache(force=False)
        if cache:
            return cache

        response = self.fetch(blocking=blocking)
        if response:
            if response.status_code == 200:
                self._save_to_cache(response.text)
                return response.text
            else:
                error = {
                    "__error__": "Failed to fetch text",
                    "status_code": response.status_code,
                    "text": response.text,
                    "headers": response.headers,
                    "reason": response.reason_phrase
                }
                error_text = json.dumps(error, indent=2)
                _error(f"Error fetching text from {self.url}:\n{error_text}")
                self._save_to_cache(error_text)  # Cache the error response
                return error_text
        return None

    def fetch_json(self, blocking=True):
        text = self.fetch_text(blocking=blocking)
        if text:
            try:
                result = json.loads(text)
                return result
            except Exception as e:
                response = {
                    "__error__": "Failed to parse JSON",
                    "status_code": 500,
                    "text": str(e),
                    "headers": {},
                    "reason": "PyMirror Exception"
                }
                return response
        return None
