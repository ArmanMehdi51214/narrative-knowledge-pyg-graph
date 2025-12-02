# graph_builder/node_builder.py

"""
Node Builder for Narrative Knowledge Graph.

Takes raw Wikidata entities and builds normalized node dictionaries
with:
- id
- label
- description
- summary (from Wikipedia)
- atu_index
- wikipedia_title
- wikipedia_url
- tags
- embedding (None for now)
- source_genre  <-- NEW FIELD (ATU_Folklore, SciFi_Theme, Game_Mechanic)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import logging


logger = logging.getLogger(__name__)


@dataclass
class Node:
    id: str
    label: str
    description: str
    summary: Optional[str]
    atu_index: Optional[str]
    wikipedia_title: Optional[str]
    wikipedia_url: Optional[str]
    tags: List[str]
    embedding: Optional[List[float]]
    source_genre: str = "Unknown"   # <-- ADDED HERE


class NodeBuilder:
    """
    Converts raw Wikidata results + Wikipedia summaries
    into unified Node dataclass objects.
    """

    def __init__(self, wiki_client):
        self.wiki = wiki_client

    # ------------------------------------------------------------------
    def build_nodes(self, raw_entities: List[Dict[str, Any]]) -> List[Node]:
        """
        Convert raw Wikidata dict results into Node objects.
        Wikipedia summary is fetched here.
        """
        nodes: List[Node] = []

        for entity in raw_entities:
            qid = entity["id"]
            label = entity.get("label", "")
            description = entity.get("description", "")
            atu = entity.get("atu_index")
            wiki_title = entity.get("wikipedia_title")
            wiki_url = entity.get("wikipedia_url")
            genre = entity.get("_source_genre", "Unknown")  # <-- READING GENRE SET BY MULTI-BUILDER

            # --- Fetch Wikipedia summary ----------------------------------------------------
            summary = None
            if wiki_title:
                try:
                    wiki_info = self.wiki.fetch_summary(wiki_title)
                    summary = wiki_info.get("summary")
                except Exception as e:
                    logger.warning(f"Failed to fetch summary for {wiki_title}: {e}")

            # --- Construct Node ------------------------------------------------------------
            node = Node(
                id=qid,
                label=label,
                description=description,
                summary=summary,
                atu_index=atu,
                wikipedia_title=wiki_title,
                wikipedia_url=wiki_url,
                tags=[],
                embedding=None,
                source_genre=genre
            )

            nodes.append(node)

        logger.info(f"Built {len(nodes)} nodes.")
        return nodes
