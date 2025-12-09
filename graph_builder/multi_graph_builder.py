# graph_builder/multi_graph_builder.py

import logging
from typing import Optional, List, Dict, Any

from graph_builder.node_builder import NodeBuilder
from graph_builder.edge_builder import EdgeBuilder
from graph_builder.graph_validator import GraphValidator

from wd_api.wikidata_client import WikidataClient
from wiki_api.wikipedia_client import WikipediaClient


logger = logging.getLogger(__name__)


class MultiGraphBuilder:
    """
    Builds a unified graph from multiple Wikidata categories:
    - Folklore (ATU)
    - Sci-Fi Themes
    - Video Game Mechanics
    
    Each category is tagged with a clean `source_genre` label.
    """

    CATEGORY_MAP = {
        "folklore": ("ATU_Folklore", "fetch_folklore"),
        "scifi": ("SciFi_Theme", "fetch_scifi_themes"),
        "game": ("Game_Mechanic", "fetch_videogame_mechanics"),
    }

    def __init__(self):
        self.wd = WikidataClient()
        self.wiki = WikipediaClient()
        self.node_builder = NodeBuilder(self.wiki)
        self.edge_builder = EdgeBuilder()
        self.validator = GraphValidator()

    # -------------------------------------------------------------
    # MAIN BUILD METHOD
    # -------------------------------------------------------------
    def build(
        self,
        limits: Dict[str, int]
    ) -> Dict[str, Any]:

        all_nodes = []
        all_edges = []

        logger.info("=== MULTI-CATEGORY GRAPH BUILD STARTED ===")

        # -----------------------------
        # 1. FETCH + BUILD NODES
        # -----------------------------
        for key, (genre_tag, fn_name) in self.CATEGORY_MAP.items():

            if key not in limits:
                logger.warning(f"No limit provided for category '{key}', skipping.")
                continue

            limit = limits[key]
            fetch_fn = getattr(self.wd, fn_name)

            logger.info(f"\n--- Fetching {key} ({limit} items) ---")
            raw_items = fetch_fn(limit=limit)

            logger.info(f"Fetched {len(raw_items)} raw entities")

            nodes = self.node_builder.build_nodes(
                raw_entities=raw_items,
                source_genre=genre_tag,
            )

            logger.info(f"Built {len(nodes)} nodes for category '{genre_tag}'")

            all_nodes.extend(nodes)

        logger.info(f"\n=== TOTAL NODES COLLECTED: {len(all_nodes)} ===")

        # -----------------------------
        # 2. BUILD EDGES (Cross-category allowed)
        # -----------------------------
        all_edges = self.edge_builder.build_edges(all_nodes)
        logger.info(f"=== TOTAL EDGES BUILT: {len(all_edges)} ===")

        # -----------------------------
        # 3. VALIDATE GRAPH
        # -----------------------------
        graph = {
            "nodes": all_nodes,
            "edges": all_edges,
        }

        graph = self.validator.validate(graph)

        logger.info("=== MULTI-CATEGORY GRAPH BUILD COMPLETED ===")

        return graph
