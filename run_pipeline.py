# run_pipeline.py

from graph_builder.multi_graph_builder import MultiGraphBuilder
from graph_builder.graph_validator import GraphValidator
from embeddings.embedder import EmbeddingGenerator
from export.json_exporter import JSONExporter
from pyg_conversion.pyg_converter import convert_to_pyg

from wd_api.wikidata_client import WikidataClient


print("\n=== UNIFIED NARRATIVE GRAPH PIPELINE ===")

# Step 1 — Clients
wd = WikidataClient()
validator = GraphValidator()
exporter = JSONExporter(output_dir="output")
embedder = EmbeddingGenerator()

# Step 2 — Multi-category unified builder
mb = MultiGraphBuilder()

graph = mb.build_multi([
    (wd.fetch_folklore, "ATU_Folklore", 1500),
    (wd.fetch_scifi_themes, "SciFi_Theme", 800),
    (wd.fetch_videogame_mechanics, "Game_Mechanic", 700)
])

# Step 3 — Embeddings (single pass)
embedder.embed_nodes(graph["nodes"])

# Step 4 — Validate final graph
graph = validator.validate(graph)

# Step 5 — Export JSON (unified)
exporter.export(graph, filename="narrative_graph_unified.json")

# Step 6 — Convert to PyG
convert_to_pyg(graph, output_dir="pyg_output_unified")

print("\n=== PIPELINE COMPLETE: UNIFIED GRAPH READY ===")
