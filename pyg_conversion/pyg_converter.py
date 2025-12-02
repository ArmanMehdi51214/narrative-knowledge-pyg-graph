# pyg_conversion/pyg_converter.py

"""
Convert narrative_graph.json (our node/edge dataset) into a PyTorch Geometric
InMemoryDataset object.

Produces:
- graph_pyg.pt  (PyG Data object)
- id2idx.pkl    (node_id → index mapping)
"""

from __future__ import annotations
import torch
from torch_geometric.data import Data, InMemoryDataset
import pickle
import os
from typing import Dict, List, Any


# ---------------------------------------------------------
# Relation Encoding
# ---------------------------------------------------------
RELATION_MAP = {
    "is_a": 0,
    "associated_with": 1,
    "inspired_by": 2,
    "based_on": 3,
}


# ---------------------------------------------------------
# Utility conversion functions
# ---------------------------------------------------------

def build_id_index_map(nodes: List[Dict[str, Any]]) -> Dict[str, int]:
    """Map node IDs (Q-codes) → integer indices."""
    return {node["id"]: idx for idx, node in enumerate(nodes)}


def make_feature_matrix(nodes: List[Dict[str, Any]]) -> torch.Tensor:
    """
    Convert embeddings into a PyTorch float tensor.
    shape: [num_nodes, 384]
    """
    matrix = [node["embedding"] for node in nodes]
    return torch.tensor(matrix, dtype=torch.float)


def make_edge_index(edges: List[Dict[str, Any]], id2idx: Dict[str, int]) -> torch.Tensor:
    """
    Convert graph edges into PyG edge_index tensor.
    shape: [2, num_edges]
    """
    src = [id2idx[e["source"]] for e in edges]
    dst = [id2idx[e["target"]] for e in edges]
    return torch.tensor([src, dst], dtype=torch.long)


def make_edge_attr(edges: List[Dict[str, Any]]) -> torch.Tensor:
    """
    Convert relation strings into integer class IDs.
    shape: [num_edges]
    """
    relation_ids = [RELATION_MAP.get(e["relation"], 1) for e in edges]
    return torch.tensor(relation_ids, dtype=torch.long)


# ---------------------------------------------------------
# PyG Dataset Class
# ---------------------------------------------------------

class NarrativeGraphPyGDataset(InMemoryDataset):
    """
    A clean InMemoryDataset wrapper for the narrative knowledge graph.
    This loads a PyG Data object that was previously saved.
    """

    def __init__(self, root: str, transform=None, pre_transform=None):
        super().__init__(root, transform, pre_transform)

        data_path = os.path.join(root, "graph_pyg.pt")
        self.data, self.slices = torch.load(data_path)

    @property
    def raw_file_names(self):
        # Not used, but required by PyG API
        return []

    @property
    def processed_file_names(self):
        return ["graph_pyg.pt"]

    def download(self):
        pass

    def process(self):
        pass


# ---------------------------------------------------------
# Main conversion function
# ---------------------------------------------------------

def convert_to_pyg(graph: Dict[str, Any], output_dir: str = "pyg_output"):
    """
    Takes the dict from GraphBuilder → Embedding → Validator
    and writes:
      - graph_pyg.pt
      - id2idx.pkl
    """

    os.makedirs(output_dir, exist_ok=True)

    nodes = graph["nodes"]
    edges = graph["edges"]

    # 1. Mapping node IDs → indices
    id2idx = build_id_index_map(nodes)

    # 2. Node feature matrix
    x = make_feature_matrix(nodes)

    # 3. Edges
    edge_index = make_edge_index(edges, id2idx)

    # 4. Edge Attributes (relation encoding)
    edge_attr = make_edge_attr(edges)

    # 5. Create PyG Data object
    data = Data(
        x=x,
        edge_index=edge_index,
        edge_attr=edge_attr,
        num_nodes=len(nodes),
    )

    # Save mapping + graph
    torch.save((data, None), os.path.join(output_dir, "graph_pyg.pt"))

    with open(os.path.join(output_dir, "id2idx.pkl"), "wb") as f:
        pickle.dump(id2idx, f)

    print("\n=== PyTorch Geometric Conversion Complete ===")
    print("Saved:", os.path.join(output_dir, "graph_pyg.pt"))
    print("Saved:", os.path.join(output_dir, "id2idx.pkl"))

    return data, id2idx
