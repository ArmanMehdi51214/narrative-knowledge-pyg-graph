import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import logging

from graph_builder.build_graph import GraphBuilder
from wd_api.wikidata_client import WikidataClient

logging.basicConfig(level=logging.INFO)

wd = WikidataClient()
gb = GraphBuilder()

print("\n=== TEST: Build Small Folklore Graph ===")
graph = gb.build(wd.fetch_videogame_mechanics, limit=50)


print(f"\nNodes: {len(graph['nodes'])}")
print(f"Edges: {len(graph['edges'])}")

print("\nSample Node:")
print(graph['nodes'][0])

print("\nSample Edge:")
if graph['edges']:
    print(graph['edges'][0])
else:
    print("No edges generated")
