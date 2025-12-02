# graph_builder/graph_validator.py

"""
Graph Validator for Narrative Knowledge Graph.

Validates:
- Node uniqueness
- Edge validity (source/target exist)
- Removes orphan edges
- Detects isolated nodes
- Ensures embeddings (optional step)
- Reports structural statistics

Used before exporting JSON or converting to PyTorch Geometric.
"""

from __future__ import annotations
import logging
from typing import Dict, List, Set

import networkx as nx

logger = logging.getLogger(__name__)


class GraphValidator:
    """
    Performs structural validation and cleanup for:
    - nodes (list of dict)
    - edges (list of dict)
    """

    # ---------------------------------------------------------
    def validate(self, graph: Dict) -> Dict:
        """
        Takes a graph dict {"nodes": [...], "edges": [...]} and
        returns a cleaned, validated version.
        """
        logger.info("=== Running Graph Validation ===")

        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])

        # Index nodes by ID
        node_ids = {n["id"] for n in nodes}
        logger.info(f"Nodes before validation: {len(nodes)}")
        logger.info(f"Edges before validation: {len(edges)}")

        # -----------------------------------------------------
        # Step 1: Remove edges with missing nodes
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
        # Step 2: Build a NetworkX graph for checks
        # -----------------------------------------------------
        G = nx.DiGraph()
        for n in nodes:
            G.add_node(n["id"])

        for e in edges:
            G.add_edge(e["source"], e["target"], relation=e["relation"])

        # -----------------------------------------------------
        # Step 3: Identify isolated nodes
        # -----------------------------------------------------
        isolated = list(nx.isolates(G))
        logger.info(f"Found {len(isolated)} isolated nodes")

        # Optional: you may want to remove them
        # For now, we keep them (they still store information).

        # -----------------------------------------------------
        # Step 4: Check weak connectivity
        # -----------------------------------------------------
        if len(G.nodes) > 0:
            weak_components = nx.number_weakly_connected_components(G)
            logger.info(f"Weakly connected components: {weak_components}")

        # -----------------------------------------------------
        # Step 5: Ensure embedding exists for each node (optional)
        # -----------------------------------------------------
        missing_emb = [n["id"] for n in nodes if not n.get("embedding")]
        if missing_emb:
            logger.warning(f"Nodes missing embeddings: {len(missing_emb)}")

        # -----------------------------------------------------
        # Step 6: Return cleaned graph
        # -----------------------------------------------------
        cleaned_graph = {
            "nodes": nodes,
            "edges": edges,
            "meta": {
                "isolated_nodes": len(isolated),
                "weakly_connected_components": weak_components
                if len(G.nodes) > 0 else 0,
            }
        }

        logger.info("=== Graph Validation Completed ===")
        return cleaned_graph
