# run_pipeline.py

import logging
from embeddings.embedder import EmbeddingGenerator
from export.json_exporter import JSONExporter
from pyg_conversion.pyg_converter import convert_to_pyg

from graph_builder.multi_graph_builder import MultiGraphBuilder
from graph_builder.node_builder import Node   # Needed for dict→Node conversion

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -----------------------------------------------------------
# Utility: Convert dict node → Node dataclass (if needed)
# -----------------------------------------------------------
def dict_to_node(d):
    return Node(
        id=d["id"],
        label=d["label"],
        description=d["description"],
        summary=d["summary"],
        atu_index=d["atu_index"],
        wikipedia_title=d["wikipedia_title"],
        wikipedia_url=d["wikipedia_url"],
        tags=d.get("tags", []),
        embedding=d.get("embedding"),
        source_genre=d.get("source_genre"),
    )


if __name__ == "__main__":
    print("\n=== UNIFIED NARRATIVE GRAPH PIPELINE ===")

    # ------------------------------------------------
    # CATEGORY LIMITS (client-approved)
    # ------------------------------------------------
    limits = {
        "folklore": 1500,
        "scifi": 800,
        "game": 700,
    }

    # ------------------------------------------------
    # 1. BUILD MULTI-CATEGORY GRAPH
    # ------------------------------------------------
    builder = MultiGraphBuilder()
    graph = builder.build(limits=limits)

    print(f"Nodes: {len(graph['nodes'])}")
    print(f"Edges: {len(graph['edges'])}")

    # ------------------------------------------------
    # 2. SAFETY: Convert dict nodes → Node objects
    # (Fixes 'dict has no attribute summary' issue)
    # ------------------------------------------------
    if graph["nodes"] and isinstance(graph["nodes"][0], dict):
        print("⚠️ Nodes are dicts — converting back to Node dataclass...")
        graph["nodes"] = [dict_to_node(n) for n in graph["nodes"]]
    else:
        print("✔ Nodes are valid Node objects.")

    # ------------------------------------------------
    # 3. EMBEDDINGS
    # ------------------------------------------------
    embedder = EmbeddingGenerator()
    embedder.embed_nodes(graph["nodes"])

    # ------------------------------------------------
    # 4. EXPORT JSON
    # ------------------------------------------------
    exporter = JSONExporter(output_dir="output")
    exporter.export(graph, filename="narrative_graph_unified.json")

    # ------------------------------------------------
    # 5. PYTORCH GEOMETRIC EXPORT
    # ------------------------------------------------
    convert_to_pyg(graph, output_dir="pyg_output_unified")


    print("\n=== PIPELINE COMPLETE: UNIFIED GRAPH READY ===")
