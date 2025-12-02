"""
Lightweight Wikidata SPARQL client.

- Sends SPARQL queries to https://query.wikidata.org/sparql
- Returns cleaned Python dicts for our graph builder.
"""

from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests

from wd_api import queries

logger = logging.getLogger(__name__)

WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"

# IMPORTANT: always send a descriptive User-Agent for polite API use.
DEFAULT_USER_AGENT = "NarrativeGraphPipeline/0.1 (contact: your-email@example.com)"


class WikidataClient:
    """
    Simple client to talk to the Wikidata SPARQL endpoint.
    """

    def __init__(
        self,
        endpoint: str = WIKIDATA_SPARQL_ENDPOINT,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: int = 30,
    ) -> None:
        self.endpoint = endpoint
        self.user_agent = user_agent
        self.timeout = timeout

    # ----------------------------------------------------------------------
    # Low-level SPARQL runner
    # ----------------------------------------------------------------------
    def run_sparql(self, query: str) -> Dict[str, Any]:
        """
        Execute a SPARQL query and return the JSON response.
        """
        headers = {
            "Accept": "application/sparql-results+json",
            "User-Agent": self.user_agent,
        }

        params = {"query": query}

        resp = requests.get(
            self.endpoint,
            headers=headers,
            params=params,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()

    # ----------------------------------------------------------------------
    # High-level root fetcher for predefined QIDs
    # ----------------------------------------------------------------------
    def fetch_entities_for_root(
        self, root_qid: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch entities under a given root QID (lit archetype, sci-fi theme, etc.)
        """
        sparql = queries.make_root_query(root_qid=root_qid, limit=limit)
        data = self.run_sparql(sparql)

        results: List[Dict[str, Any]] = []

        for row in data.get("results", {}).get("bindings", []):
            entity_uri = row["entity"]["value"]
            qid = entity_uri.rsplit("/", 1)[-1]

            label = row.get("entityLabel", {}).get("value", "")
            description = row.get("entityDescription", {}).get("value", "")

            atu_index = row.get("atu", {}).get("value")
            wikipedia_title = row.get("wikipediaTitle", {}).get("value")

            wikipedia_url = None
            if wikipedia_title:
                safe_title = quote(wikipedia_title.replace(" ", "_"))
                wikipedia_url = f"https://en.wikipedia.org/wiki/{safe_title}"

            results.append(
                {
                    "id": qid,
                    "label": label,
                    "description": description,
                    "atu_index": atu_index,
                    "wikipedia_title": wikipedia_title,
                    "wikipedia_url": wikipedia_url,
                }
            )

        logger.info("Fetched %d entities under root %s", len(results), root_qid)
        return results

    # ----------------------------------------------------------------------
    # Fetch ATU folklore (independent of root QIDs)
    # ----------------------------------------------------------------------
    def fetch_folklore(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Fetch folktales that have an ATU index (P2540).
        """
        query = f"""
        SELECT ?entity ?entityLabel ?entityDescription ?atu ?wikipediaTitle WHERE {{
          ?entity wdt:P2540 ?atu .

          OPTIONAL {{
            ?sitelink schema:about ?entity ;
                      schema:isPartOf <https://en.wikipedia.org/> ;
                      schema:name ?wikipediaTitle .
          }}

          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }}
        LIMIT {limit}
        """

        raw = self.run_sparql(query)["results"]["bindings"]

        cleaned = []
        for row in raw:
            cleaned.append({
                "id": row["entity"]["value"].split("/")[-1],
                "label": row.get("entityLabel", {}).get("value"),
                "description": row.get("entityDescription", {}).get("value"),
                "atu_index": row.get("atu", {}).get("value"),
                "wikipedia_title": row.get("wikipediaTitle", {}).get("value"),
                "wikipedia_url": None  # WikipediaClient will handle URL
            })

        return cleaned

    # ----------------------------------------------------------------------
    # Convenience wrappers for other narrative categories
    # ----------------------------------------------------------------------
    def fetch_literary_archetypes(self, limit: Optional[int] = None):
        return self.fetch_entities_for_root(queries.LITERARY_ARCHETYPE_QID, limit)

    def fetch_scifi_themes(self, limit: Optional[int] = None):
        return self.fetch_entities_for_root(queries.SCIFI_THEME_QID, limit)

    def fetch_videogame_mechanics(self, limit: Optional[int] = None):
        return self.fetch_entities_for_root(queries.VIDEOGAME_MECHANIC_QID, limit)