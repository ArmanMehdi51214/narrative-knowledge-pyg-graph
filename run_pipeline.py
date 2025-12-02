# run_pipeline.py

from graph_builder.build_graph import GraphBuilder
from graph_builder.graph_validator import GraphValidator
from embeddings.embedder import EmbeddingGenerator
from export.json_exporter import JSONExporter
from pyg_conversion.pyg_converter import convert_to_pyg

from wd_api.wikidata_client import WikidataClient

print("\n=== Narrative Graph Pipeline Running ===")

# Step 1 — Fetch from Wikidata
wd = WikidataClient()
gb = GraphBuilder()
validator = GraphValidator()
exporter = JSONExporter(output_dir="output")

# Choose your category
graph = gb.build(fetch_function=wd.fetch_folklore, limit=300)

# Step 2 — Embedding
embedder = EmbeddingGenerator()
embedder.embed_nodes(graph["nodes"])

# Step 3 — Validate
graph = validator.validate(graph)

# Step 4 — JSON Export
exporter.export(graph, filename="narrative_graph.json")

# Step 5 — Convert to PyTorch Geometric
convert_to_pyg(graph, output_dir="pyg_output")

print("\n=== Pipeline Complete ===")
