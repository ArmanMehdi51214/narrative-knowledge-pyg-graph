# graph_builder/multi_graph_builder.py

from __future__ import annotations
from typing import List, Tuple, Callable, Dict, Any
import logging

from graph_builder.build_graph import GraphBuilder
from graph_builder.node_builder import NodeBuilder
from graph_builder.edge_builder import EdgeBuilder
from wiki_api.wikipedia_client import WikipediaClient


class MultiGraphBuilder:

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

        # internal components
        self.wiki = WikipediaClient()
        self.node_builder = NodeBuilder(self.wiki)
        self.edge_builder = EdgeBuilder()

        # re-use GraphBuilder functions for merging logic
        self.single_builder = GraphBuilder()

    # ------------------------------------------------------------------
    # Build merged graph from multiple (fetch_fn, tag, limit) entries
    # ------------------------------------------------------------------
    def build_multi(
        self,
        categories: List[Tuple[Callable, str, int]]
    ) -> Dict[str, Any]:
        """
        categories = [
           (wd.fetch_folklore, "ATU_Folklore", 1500),
           (wd.fetch_scifi_themes, "SciFi_Theme", 800),
           (wd.fetch_videogame_mechanics, "Game_Mechanic", 700)
        ]

        Returns a fully merged graph with:
        - nodes tagged by source_genre
        - unified node list
        - unified edge list
        """

        all_nodes = []
        all_raw_entities = []

        self.logger.info("=== MULTI-CATEGORY GRAPH BUILD START ===")

        # ------------------------------------------------------------------
        # 1. Fetch and build nodes per category
        # ------------------------------------------------------------------
        for fetch_fn, genre_tag, limit in categories:
            self.logger.info(f"Fetching category {genre_tag} (limit={limit})")

            raw = fetch_fn(limit=limit)
            if not raw:
                self.logger.warning(f"No entities found for category {genre_tag}")
                continue

            # add genre tag before building nodes
            for r in raw:
                r["_source_genre"] = genre_tag

            all_raw_entities.extend(raw)

            self.logger.info(f"Fetched {len(raw)} entities for {genre_tag}")

        # ------------------------------------------------------------------
        # 2. Build all nodes
        # ------------------------------------------------------------------
        self.logger.info("Building nodes for ALL categories...")
        nodes = self.node_builder.build_nodes(all_raw_entities)

        # Inject source genre into node dictionaries
        for node, raw in zip(nodes, all_raw_entities):
            node.source_genre = raw.get("_source_genre", "Unknown")

        # Convert dataclass nodes → dictionaries (GraphBuilder's format)
        node_dicts = []
        for n in nodes:
            node_dicts.append({
                "id": n.id,
                "label": n.label,
                "description": n.description,
                "summary": n.summary,
                "atu_index": n.atu_index,
                "wikipedia_title": n.wikipedia_title,
                "wikipedia_url": n.wikipedia_url,
                "tags": n.tags,
                "embedding": None,
                "source_genre": n.source_genre
            })

        # ------------------------------------------------------------------
        # 3. Build edges using merged node list
        # ------------------------------------------------------------------
        self.logger.info("Building edges across all categories...")
        edges = self.edge_builder.build_edges(node_dicts)

        # ------------------------------------------------------------------
        # 4. FINAL unified graph
        # ------------------------------------------------------------------
        graph = {
            "nodes": node_dicts,
            "edges": edges,
            "meta": {
                "total_nodes": len(node_dicts),
                "total_edges": len(edges),
                "categories": [c[1] for c in categories],
            }
        }

        self.logger.info("=== MULTI-CATEGORY GRAPH BUILD COMPLETE ===")
        self.logger.info(f"Total Nodes = {len(node_dicts)}")
        self.logger.info(f"Total Edges = {len(edges)}")

        return graph
