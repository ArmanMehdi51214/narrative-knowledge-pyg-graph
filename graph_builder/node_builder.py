# graph_builder/node_builder.py

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
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
    source_genre: str


class NodeBuilder:

    def __init__(self, wiki_client):
        self.wiki = wiki_client

    def build_nodes(
        self,
        raw_entities: List[Dict[str, Any]],
        source_genre: str,
    ) -> List[Node]:

        nodes: List[Node] = []

        for ent in raw_entities:
            qid = ent.get("id")
            label = ent.get("label", "")
            description = ent.get("description", "")
            atu_index = ent.get("atu_index")
            wikipedia_title = ent.get("wikipedia_title")
            wikipedia_url = ent.get("wikipedia_url")

            # ---- FIXED PART: fetch *string* summary, not dict ----
            summary_text: Optional[str] = None
            if wikipedia_title:
                try:
                    summary_data = self.wiki.fetch_summary(wikipedia_title)
                    if isinstance(summary_data, dict):
                        summary_text = summary_data.get("summary") or ""
                    elif isinstance(summary_data, str):
                        summary_text = summary_data
                except Exception as e:
                    logger.error(f"Failed to fetch summary for {label}: {e}")
                    summary_text = ""
            else:
                summary_text = ""

            node = Node(
                id=qid,
                label=label,
                description=description,
                summary=summary_text,
                atu_index=atu_index,
                wikipedia_title=wikipedia_title,
                wikipedia_url=wikipedia_url,
                tags=[],
                embedding=None,
                source_genre=source_genre,
            )

            nodes.append(node)

        logger.info(f"Built {len(nodes)} nodes for category {source_genre}.")
        return nodes
