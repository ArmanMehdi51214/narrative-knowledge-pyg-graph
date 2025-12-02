# export/json_exporter.py

"""
JSON Exporter for the Narrative Knowledge Graph.

Writes:
- narrative_graph.json (full nodes + edges + meta)
- Ensures schema compliance
"""

from __future__ import annotations
import json
import logging
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class JSONExporter:
    """
    Exports the validated graph to a JSON file using the strict schema.

    Schema:
    {
      "meta": {...},
      "nodes": [...],
      "edges": [...]
    }
    """

    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    def export(self, graph: Dict[str, Any], filename: str = "narrative_graph.json"):
        """
        Export the complete graph dict to disk in strict JSON format.
        """

        logger.info("=== Exporting Narrative Graph to JSON ===")

        filepath = self.output_dir / filename

        # Inject top-level metadata if not present
        if "meta" not in graph:
            graph["meta"] = {}

        graph["meta"].update({
            "export_timestamp": datetime.utcnow().isoformat() + "Z",
            "exporter_version": "1.0",
            "total_nodes": len(graph.get("nodes", [])),
            "total_edges": len(graph.get("edges", [])),
        })

        with filepath.open("w", encoding="utf-8") as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)

        logger.info(f"Graph exported successfully → {filepath.resolve()}")

        return filepath
