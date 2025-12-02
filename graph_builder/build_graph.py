# Call NodeBuilder + EdgeBuilder, and output a combined {"nodes": [...], "edges": [...]} structure.
# graph_builder/build_graph.py

import logging
from typing import Dict, List

from wd_api.wikidata_client import WikidataClient
from wiki_api.wikipedia_client import WikipediaClient

from graph_builder.node_builder import NodeBuilder
from graph_builder.edge_builder import EdgeBuilder


class GraphBuilder:
    """
    Orchestrates the full construction of the narrative knowledge graph.
    Fetches raw data from Wikidata, enriches it with Wikipedia summaries,
    then builds nodes and edges according to the required schema.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.wd = WikidataClient()
        self.wiki = WikipediaClient()

        self.node_builder = NodeBuilder(wiki_client=self.wiki)
        self.edge_builder = EdgeBuilder()

    # ----------------------------------------------------------------------
    # Public API: Build graph for any Wikidata root or SPARQL query function
    # ----------------------------------------------------------------------
    def build(self, fetch_function, limit: int = 3000) -> Dict:
        """
        Build the complete narrative graph.

        Parameters
        ----------
        fetch_function : callable
            A WikidataClient method reference, e.g.:
                wd.fetch_folklore
                wd.fetch_scifi_themes
                wd.fetch_videogame_mechanics

        limit : int
            Maximum number of entities to fetch.

        Returns
        -------
        dict
            {
              "nodes": [...],
              "edges": [...]
            }
        """

        self.logger.info("=== Fetching raw entities from Wikidata ===")
        raw_entities = fetch_function(limit=limit)

        if not raw_entities:
            self.logger.error("No entities retrieved. Graph cannot be built.")
            return {"nodes": [], "edges": []}

        self.logger.info(f"Fetched {len(raw_entities)} raw entities")

        # ------------------------------------------------------------
        # 1. Build nodes
        # ------------------------------------------------------------
        self.logger.info("=== Building nodes ===")
        nodes = self.node_builder.build_nodes(raw_entities)

        if not nodes:
            self.logger.error("NodeBuilder returned no nodes.")
            return {"nodes": [], "edges": []}

        node_ids = [n.id for n in nodes]
        self.logger.info(f"Constructed {len(nodes)} nodes")

        # ------------------------------------------------------------
        # 2. Build edges
        # ------------------------------------------------------------
        self.logger.info("=== Building edges ===")
        edges = self.edge_builder.build_edges(node_ids)

        self.logger.info(f"Constructed {len(edges)} edges")

        # ------------------------------------------------------------
        # 3. Convert nodes into JSON-serializable dicts
        # ------------------------------------------------------------
        node_dicts = [self._node_to_dict(n) for n in nodes]

        graph = {
            "nodes": node_dicts,
            "edges": edges,
        }

        self.logger.info("=== Graph building completed ===")
        return graph

    # ----------------------------------------------------------------------
    # Convert Node dataclass → plain dict for JSON export
    # ----------------------------------------------------------------------
    @staticmethod
    def _node_to_dict(node):
        return {
            "id": node.id,
            "label": node.label,
            "description": node.description,
            "summary": node.summary,
            "atu_index": node.atu_index,
            "wikipedia_title": node.wikipedia_title,
            "wikipedia_url": node.wikipedia_url,
            "tags": node.tags,
            "embedding": node.embedding,  # added later by embedder
        }
