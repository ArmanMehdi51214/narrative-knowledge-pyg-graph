# export/json_exporter.py

import json
import os
from typing import Any, Dict, List
from dataclasses import asdict
import logging

logger = logging.getLogger(__name__)


class JSONExporter:

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _node_to_dict(self, node_obj):
        """
        Convert Node dataclass → plain dict.
        """
        try:
            return asdict(node_obj)
        except Exception:
            # already a dict
            return node_obj

    def _edge_to_dict(self, edge_obj):
        """
        Edges are already dicts, but we normalize them anyway.
        """
        return dict(edge_obj)

    # ---------------------------------------------------------------
    def export(self, graph: Dict[str, Any], filename: str = "graph.json"):
        """
        Saves the graph to a JSON file.
        Handles Node dataclasses by converting them to dicts.
        """
        logger.info("=== Exporting Narrative Graph to JSON ===")

        nodes = graph.get("nodes", [])
        edges = graph.get("edges", [])
        meta = graph.get("meta", {})

        # Convert nodes to dicts
        node_dicts = [self._node_to_dict(n) for n in nodes]

        # Convert edges to dicts
        edge_dicts = [self._edge_to_dict(e) for e in edges]

        clean_graph = {
            "nodes": node_dicts,
            "edges": edge_dicts,
            "meta": meta,
        }

        output_path = os.path.join(self.output_dir, filename)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(clean_graph, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved JSON to: {output_path}")
        return output_path
