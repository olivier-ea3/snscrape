import logging
import re
import time

import requests
from torpy import TorClient
from torpy.http.adapter import TorHttpAdapter

logger = logging.getLogger(__name__)


class TokenExpiryException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class RefreshTokenException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class Token:
    def __init__(self, use_tor=True):
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0"
            }
        )
        self.use_tor = use_tor
        self._retries = 5
        self._timeout = 10
        self._hops_count = 2
        self._guard = None
        self._tor = None

        self.url = "https://twitter.com"

    def _close_tor_connexion(self):
        if self._guard:
            self._guard.close()

        if self._tor:
            self._tor.close()

    def _activate_tor_proxy(self):
        logger.info(f"TOR Proxy Activation")

        self._tor = TorClient()
        self._guard = self._tor.get_guard()
        self._adapter = TorHttpAdapter(
            self._guard, self._hops_count, retries=self._retries
        )

        self._session.mount("http://", self._adapter)
        self._session.mount("https://", self._adapter)

    def _request(self):
        for attempt in range(self._retries + 1):
            # The request is newly prepared on each retry because of potential cookie updates.
            req = self._session.prepare_request(requests.Request("GET", self.url))
            logger.debug(f"Retrieving {req.url}")
            try:
                if self.use_tor:
                    self._activate_tor_proxy()
                    logger.debug(f"TOR Proxy activated !")
                else:
                    logger.debug(f"TOR Proxy NOT activated !")

                r = self._session.send(req, allow_redirects=True, timeout=self._timeout)
            except requests.exceptions.RequestException as exc:
                if attempt < self._retries:
                    retrying = ", retrying"
                    level = logger.WARNING
                else:
                    retrying = ""
                    level = logger.ERROR
                logger.log(level, f"Error retrieving {req.url}: {exc!r}{retrying}")
            else:
                success, msg = (True, None)
                msg = f": {msg}" if msg else ""

                if success:
                    logger.debug(f"{req.url} retrieved successfully{msg}")
                    return r
            if attempt < self._retries:
                # TODO : might wanna tweak this back-off timer
                sleep_time = 2.0 * 2 ** attempt
                logger.info(f"Waiting {sleep_time:.0f} seconds")
                time.sleep(sleep_time)
        else:
            msg = f"{self._retries + 1} requests to {self.url} failed, giving up."
            logger.fatal(msg)
            self.guest_token = None
            raise RefreshTokenException(msg)

    def refresh(self):
        logger.debug("Retrieving guest token")
        self.res = self._request()
        match = re.search(r'\("gt=(\d+);', self.res.text)
        if match:
            logger.debug("Found guest token in HTML")
            self.guest_token = str(match.group(1))
        else:
            self.guest_token = None
            raise RefreshTokenException("Could not find the Guest token in HTML")
