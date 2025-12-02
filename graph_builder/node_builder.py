# Take raw Wikidata + Wikipedia data → output clean node objects that match your ML schema.
# graph_builder/node_builder.py

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import logging


@dataclass
class Node:
    """
    Internal representation of a graph node before exporting to JSON.
    This structure is simple and ML-friendly.
    """
    id: str
    label: str
    description: str = ""
    summary: str = ""
    wikipedia_title: Optional[str] = None
    wikipedia_url: Optional[str] = None
    atu_index: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    embedding: Optional[List[float]] = None  # will be added later


class NodeBuilder:
    """
    Converts raw Wikidata + Wikipedia data into normalized Node objects.
    """

    def __init__(self, wiki_client=None):
        self.wiki_client = wiki_client
        self.logger = logging.getLogger(self.__class__.__name__)

    # -------------------------------------------------
    # Main public method
    # -------------------------------------------------
    def build_nodes(self, raw_entities: List[Dict]) -> List[Node]:
        """
        Build normalized Node objects from raw Wikidata API output.
        """
        nodes = []

        for ent in raw_entities:
            node = self._build_single_node(ent)
            if node is None:
                continue

            # Fetch Wikipedia summary if available
            if node.wikipedia_title and self.wiki_client:
                summary_data = self._fetch_wikipedia_summary(node.wikipedia_title)
                if summary_data:
                    node.summary = summary_data.get("summary", "")
                    node.wikipedia_url = summary_data.get("url")

            # Fallback: summary = description if no Wikipedia
            if not node.summary:
                node.summary = node.description or node.label

            nodes.append(node)

        self.logger.info(f"Built {len(nodes)} nodes.")
        return nodes

    # -------------------------------------------------
    # Build a single node
    # -------------------------------------------------
    def _build_single_node(self, ent: Dict) -> Optional[Node]:
        """
        Create a Node object from a single SPARQL entity result.
        """
        try:
            qid = ent.get("id")
            label = ent.get("label", qid)
            description = ent.get("description", "")
            atu = ent.get("atu_index")
            wiki_title = ent.get("wikipedia_title")

            node = Node(
                id=qid,
                label=label,
                description=description,
                atu_index=atu,
                wikipedia_title=wiki_title
            )
            return node

        except Exception as e:
            self.logger.error(f"Failed to build node for entity {ent}: {e}")
            return None

    # -------------------------------------------------
    # Fetch Wikipedia summary
    # -------------------------------------------------
    def _fetch_wikipedia_summary(self, title: str) -> Optional[Dict]:
        try:
            return self.wiki_client.fetch_summary(title)
        except Exception as e:
            self.logger.warning(f"Wikipedia summary fetch failed for {title}: {e}")
            return None
