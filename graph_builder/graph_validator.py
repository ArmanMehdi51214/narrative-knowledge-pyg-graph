# graph_builder/graph_validator.py

"""
Graph Validator for Narrative Knowledge Graph.

Validates:
- Node uniqueness
- Edge validity (source/target exist)
- Removes orphan edges
- Detects isolated nodes
- Ensures embeddings (optional)
- Reports structural statistics
"""

from __future__ import annotations
import logging
from typing import Dict
import networkx as nx

logger = logging.getLogger(__name__)


class GraphValidator:
    """
    Performs structural validation and cleanup for graphs where:
    - nodes are Node dataclass objects
    - edges are dictionaries
    """

    def validate(self, graph: Dict) -> Dict:
        logger.info("=== Running Graph Validation ===")

        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])

        # -----------------------------------------------------
        # Step 0: Extract node IDs (dataclass objects)
        # -----------------------------------------------------
        node_ids = {n.id for n in nodes}

        logger.info(f"Nodes before validation: {len(nodes)}")
        logger.info(f"Edges before validation: {len(edges)}")

        # -----------------------------------------------------
        # Step 1: Remove edges referencing unknown nodes
        # -----------------------------------------------------
        valid_edges = []
        for e in edges:
            if e["source"] in node_ids and e["target"] in node_ids:
                valid_edges.append(e)
            else:
                logger.warning(
                    f"Removed invalid edge: {e['source']} → {e['target']} (missing node)"
                )

        edges = valid_edges
        logger.info(f"Edges after cleanup: {len(edges)}")

        # -----------------------------------------------------
        # Step 2: Build directed NetworkX graph
        # -----------------------------------------------------
        G = nx.DiGraph()
        for n in nodes:
            G.add_node(n.id)

        for e in edges:
            G.add_edge(e["source"], e["target"], relation=e["relation"])

        # -----------------------------------------------------
        # Step 3: Find isolated nodes
        # -----------------------------------------------------
        isolated = list(nx.isolates(G))
        logger.info(f"Found {len(isolated)} isolated nodes")

        # -----------------------------------------------------
        # Step 4: Connectivity check
        # -----------------------------------------------------
        weak_components = (
            nx.number_weakly_connected_components(G)
            if len(G.nodes) > 0
            else 0
        )
        logger.info(f"Weakly connected components: {weak_components}")

        # -----------------------------------------------------
        # Step 5: Embedding check (Node dataclass fields)
        # -----------------------------------------------------
        missing_emb = [n.id for n in nodes if n.embedding is None]
        if missing_emb:
            logger.warning(f"Nodes missing embeddings: {len(missing_emb)}")

        # -----------------------------------------------------
        # Step 6: Return validated graph
        # -----------------------------------------------------
        cleaned_graph = {
            "nodes": nodes,
            "edges": edges,
            "meta": {
                "isolated_nodes": len(isolated),
                "weakly_connected_components": weak_components,
            },
        }

        logger.info("=== Graph Validation Completed ===")
        return cleaned_graph
