import os
import time
import httpx
import asyncio
import json

import inspect
from pymirror.pmtimer import PMTimer
from pymirror.pmlogger import _debug, _print, _error, trace
from pymirror.utils import SafeNamespace

# @trace
class PMWebApi:
    def __init__(self, url: str, poll_secs: int = 3600, cache_file: str = None):
        self.url = url
        self.cache_file = cache_file
        self.poll_secs = poll_secs  # Default polling rate in seconds
        self.timer = PMTimer(1)
        self.async_loop = asyncio.get_event_loop()
        self.task = None
        self.cache_info = SafeNamespace(text=None)
        self.async_delay = 0.001
        self.set_httpx()
        self.error = None

    def set_httpx(self, method="get", headers={"Accept": "application/json"}, params={}, data=None, json=None, timeout_secs=2):
        self.httpx = SafeNamespace()
        self.httpx.method = method
        self.httpx.headers = headers
        self.httpx.params = params
        self.httpx.data = data
        self.httpx.json = json
        self.httpx.timeout_secs = timeout_secs
        return self.httpx

    def is_from_cache(self):
        return self.cache_info.file != None

    def _get_fresh_cache_filename(self):
        self.cache_info = SafeNamespace()
        self.cache_info.file = self.cache_file
        self.cache_info.exists = os.path.exists(self.cache_file)
        self.cache_info.size = os.path.getsize(self.cache_file) if self.cache_info.exists else 0
        self.cache_info.last_modified = os.path.getmtime(self.cache_file) if self.cache_info.exists else 0
        # convert last_modified epoch into datetime string
        self.cache_info.last_date = time.ctime(self.cache_info.last_modified)
        if (
           not self.cache_info.file
           or not self.cache_info.exists
           or self.cache_info.size == 0
           or self.poll_secs <= 0):
            #if there's no cache file, return None
            return None
        if (self.cache_info.last_modified + self.poll_secs) < time.time():
            return None  # Cache is too old, do not use it
        return self.cache_file

    def _fetch_from_file_cache(self):
        # Read the cached file
        text = None
        cache_file = self._get_fresh_cache_filename()
        if cache_file:
            with open(cache_file, 'r') as file:
                text = file.read()
        else:
            self.cache_info = SafeNamespace() ## reset the cache_info because we didn't read from the cache
        self.cache_info.text = text
        return text

    def _fetch_fresh_cache(self):
        text = None
        if not self.timer.is_timedout():
            # if not timed out, return last cache
            text = self.cache_info.text
            if not text:
                ## try to get it from the cache_file if the stored cache_info.text is None
                text = self._fetch_from_file_cache()
        return text

    def _save_to_cache(self, text):
        self.timer.set_timeout(self.poll_secs * 1000)
        if self.cache_info.text != text:
            _debug(f"Cache updated for {self.url}, size: {len(text) if text else 0} bytes")
            _debug(f"Cache text: {self.cache_info.text}")
            _debug(f"Saving to cache: {self.cache_file}")
            self.cache_info.text = text
            if text and self.cache_file:
                # Ensure the directory exists
                # os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
                # Write the text to the cache file
                with open(self.cache_file, 'w') as file:
                    file.write(text)

    async def _async_fetch(self):
        async with httpx.AsyncClient(timeout=self.httpx.timeout_secs) as client:
            method = self.httpx.method.upper()
            _debug(f"Fetching {self.url} with method {method}...")
            # Select the method dynamically
            _debug(f"...headers: {self.httpx.headers}, params: {self.httpx.params}")
            response = await client.request(
                method,
                self.url,
                headers=self.httpx.headers,
                params=self.httpx.params,
                data=self.httpx.data if method != "GET" else None,
                json=self.httpx.json if method != "GET" else None,
                follow_redirects=True
            )
            _debug(f"Received response from {self.url} with status code {response.status_code}")
            return response

    def start(self): 
        self.task = self.async_loop.create_task(self._async_fetch())

    def cancel(self):
        if self.task:
            self.task.cancel()
            self.task = None

    def fetch(self, blocking=True):
        try:
            if blocking:
                _debug(f"Blocking fetch from {self.url} with method {self.httpx.method}")
                self.start()
                self.async_loop.run_until_complete(self.task)
            else:
                _debug(f"Non-blocking fetch from {self.url} with method {self.httpx.method}")
                ## give asyncio some time to process
                if self.task is None:
                    self.start()
                self.async_loop.run_until_complete(asyncio.sleep(self.async_delay))
            if self.task.done():
                _debug(f"Fetch task completed for {self.url}")
                result = self.task.result()
                self.task = None
                return result
            return None
        except Exception as e:
            self.cancel()
            self.error = {
                "status_code": 500,
                "text": repr(e),
                "headers": {},
                "reason": "PyMirror Exception",
                "function": inspect.currentframe().f_code.co_name
            }
            _error(f"Error fetching from {self.url}:\n{self.error}")
            return None

    def _fetch_from_api(self, blocking=True):
        text = None
        self.error = None
        response = self.fetch(blocking=blocking)
        _debug(f"Fetch response from {self.url}: {response}")
        if response:
            _debug(f"Response status code: {response.status_code}")
            if response.status_code == 200:
                text = response.text
            else:
                self.error = {
                    "__error__": "Failed to fetch text",
                    "status_code": response.status_code,
                    "text": response.text,
                    "headers": response.headers,
                    "reason": response.reason_phrase,
                    "function": inspect.currentframe().f_code.co_name
                }
                _error(f"Error fetching text from {self.url}:\n{self.error}")
        return text

    def fetch_text(self, blocking=True):
        text = self._fetch_fresh_cache() or self._fetch_from_api(blocking)
        self._save_to_cache(text)
        return text

    def fetch_json(self, blocking=True):
        result = None
        text = self.fetch_text(blocking=blocking)
        if text:
            try:
                result = json.loads(text)
            except Exception as e:
                self.error = {
                    "__error__": "Failed to parse JSON",
                    "status_code": 500,
                    "text": repr(e),
                    "headers": {},
                    "reason": "PyMirror Exception",
                    "function": inspect.currentframe().f_code.co_name
                }
                _error(f"Error fetching json from {self.url}:\n{self.error}")
        return result

def main():
    import dotenv
    dotenv.load_dotenv('.secrets')
    api = PMWebApi("https://httpbin.org/delay/1", poll_secs=60, cache_file='./caches/tet.json')
    result = None
    while result is None:
        result = api.fetch_json(blocking=False)
        if api.error:
            _error(f"Error fetching json from {api.url}:\n{api.error}")
            break
    print(result)
    print(api.cache_info)
    if api.is_from_cache():
        print("Response is from cache")
    else:
        print("Response is not from cache")

if __name__ == "__main__":
    main()