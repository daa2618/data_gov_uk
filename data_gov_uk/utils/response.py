from __future__ import annotations

from .log_helper import BasicLogger

import requests
from urllib.parse import urlsplit, urlunsplit
import time
from pathlib import Path
from typing import Optional, Dict, Any


_bl = BasicLogger(verbose=False, log_directory=None, logger_name="RESPONSE")


class MethodError(Exception):
    pass

class Response:
    _METHODS = {"GET", "POST", "DELETE"}

    def __init__(
        self,
        url: str,
        method: str = "GET",
        *,
        session: Optional[requests.Session] = None,
        timeout: float = 30.0,
        verify: bool = True,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        data: Optional[Any] = None,
        allow_redirects: bool = True,
        trust_env: Optional[bool] = None,   # override per-request if needed
        stream: bool = False,
    ):
        self.url = url
        self.method = method.upper()
        if self.method not in self._METHODS:
            raise MethodError(f"Unsupported method: {self.method}")

        # Reuse a shared session so cookies persist (critical for IBKR gateway)
        self.session = session or requests.Session()

        # Ensure proxies don’t hijack localhost (unless you explicitly want them)
        if trust_env is not None:
            self.session.trust_env = trust_env
        else:
            self.session.trust_env = False  # safe default for localhost

        # Self-signed cert on https://localhost:5000 -> often verify=False
        self.verify = verify
        self.timeout = timeout
        self.allow_redirects = allow_redirects
        self.stream = stream

        # Don’t mutate the default header between calls
        ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118 Safari/537.36"
        base_headers = {"User-Agent": ua, "Accept": "application/json"}
        if headers:
            base_headers.update(headers)
        self.headers = base_headers

        self.params = params
        self.json = json
        self.data = data
        self._response: Optional[requests.Response] = None

    @property
    def response(self) -> requests.Response:
        if self._response is None:
            # Map to the bound method on the session
            req = getattr(self.session, self.method.lower())
            self._response = req(
                self.url,
                params=self.params,
                headers=self.headers,
                json=self.json,
                data=self.data,
                timeout=self.timeout,
                verify=self.verify,
                allow_redirects=self.allow_redirects,
                stream=self.stream,
            )
        return self._response

    def assert_response(self, await_response: bool = False, poll_interval: float = 1.0) -> requests.Response:
        """
        If await_response is True, keep retrying until we get a response without exceptions.
        Then assert HTTP 200. If not 200, raise_for_status (but after logging basics).
        """
        if self._response is None:
            if await_response:
                while self._response is None:
                    try:
                        _ = self.response
                    except Exception as e:
                        _bl.exception(f"\tTransient error: {e}. Sleeping {poll_interval}s…")
                        time.sleep(poll_interval)
                        self._response = None
                        continue
            else:
                _ = self.response

        # At this point we have a response; if not 200, show diagnostics before raising.
        if self._response.status_code != 200:
            body_preview = ""
            try:
                body_preview = self._response.text[:1000]
            except Exception:
                pass
            _bl.error(f"[HTTP {self._response.status_code}] {self.url}\nHeaders: {self._response.headers}\nBody: {body_preview}")
            self._response.raise_for_status()

        return self._response

    def get_json_from_response(self, await_response: bool = False) -> Optional[Any]:
        try:
            resp = self.assert_response(await_response=await_response)
            # Use requests’ JSON decoder (handles bytes/encoding)
            return resp.json()
        except Exception as e:
            _bl.exception(f"ERROR: Failed to get JSON from response: {e}")
            return None

    def get_base_url(self) -> str:
        splitUrl = urlsplit(self.url)
        return "://".join([splitUrl.scheme, splitUrl.netloc])

    

class GET_RESPONSE(Response):
    def __init__(self, url:str, **kwargs):
        super().__init__(method="GET", url=url, **kwargs)

class POST_RESPONSE(Response):
    def __init__(self, url:str, **kwargs):
        super().__init__(method="POST", url=url, **kwargs)