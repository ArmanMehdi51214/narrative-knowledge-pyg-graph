# wiki_api/wikipedia_client.py
"""
Wikipedia REST API Client
-------------------------

Fetches the introduction summary for a given article title using the
official Wikipedia "page summary" endpoint:

  https://en.wikipedia.org/api/rest_v1/page/summary/{title}

Returned fields are:
- title
- summary
- url (canonical Wikipedia URL)
- thumbnail (optional)
"""

from __future__ import annotations

import logging
from typing import Optional, Dict
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)


WIKIPEDIA_SUMMARY_API = (
    "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
)

DEFAULT_USER_AGENT = "NarrativeGraphPipeline/0.1 (contact: your-email@example.com)"


class WikipediaClient:
    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: int = 15,
    ) -> None:
        self.user_agent = user_agent
        self.timeout = timeout

    # ---------------------------------------------------------------
    def fetch_summary(self, title: str) -> Optional[Dict]:
        """
        Fetch the Wikipedia intro summary for a page title.
        - Automatically handles spaces → underscores
        - Handles redirects (API does it natively)
        - Returns None if not found

        Output format:
        {
            "title": "Dragon Slayer",
            "summary": "The Dragon Slayer is a folklore archetype...",
            "url": "https://en.wikipedia.org/wiki/Dragon_Slayer"
        }
        """
        if not title:
            return None

        safe_title = quote(title.replace(" ", "_"))

        url = WIKIPEDIA_SUMMARY_API.format(title=safe_title)

        logger.debug("Requesting Wikipedia summary: %s", url)

        headers = {
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }

        try:
            resp = requests.get(url, headers=headers, timeout=self.timeout)
            if resp.status_code == 404:
                return None

            resp.raise_for_status()
            data = resp.json()

            # Extract relevant fields
            extract = data.get("extract")
            canonical_url = data.get("content_urls", {})
            desktop_url = canonical_url.get("desktop", {}).get("page")

            return {
                "title": data.get("title"),
                "summary": extract,
                "url": desktop_url,
                "thumbnail": data.get("thumbnail", {}),
            }

        except Exception as e:
            logger.warning("Wikipedia request failed for '%s': %s", title, e)
            return None


# ---------------------------------------------------------------
# Optional quick test
# ---------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    w = WikipediaClient()
    result = w.fetch_summary("Dragon Slayer")

    print("\nWikipedia Result:\n", result)
