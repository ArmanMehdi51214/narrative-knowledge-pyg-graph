"""
Embedding generator using SentenceTransformers (MiniLM-L6-v2).
Nodes are plain dictionaries, not objects — this version handles dicts safely.
"""

from __future__ import annotations
import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingGenerator:

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        logger.info("Loading embedding model: %s", model_name)
        self.model = SentenceTransformer(model_name)

    # --------------------------------------------------------
    # Helper to extract the best available text for embedding
    # --------------------------------------------------------
    def _get_text_for_node(self, node: Dict[str, Any]) -> str:
        """
        Node is a dict. Use summary first, fallback to description or label.
        """
        summary = node.get("summary")
        description = node.get("description")
        label = node.get("label", "")

        if summary and summary.strip():
            return summary
        if description and description.strip():
            return description
        return label  # fallback

    # --------------------------------------------------------
    # Generate embeddings for all nodes
    # --------------------------------------------------------
    def embed_nodes(self, nodes: List[Dict[str, Any]]) -> None:
        """
        Mutates each node dict by adding node["embedding"] = list[float]
        """

        logger.info("Preparing text for %d nodes...", len(nodes))

        texts = [self._get_text_for_node(node) for node in nodes]

        logger.info("Computing embeddings... this may take a moment.")
        embeddings = self.model.encode(texts, show_progress_bar=True)

        logger.info("Assigning embeddings to node dicts.")
        for node, emb in zip(nodes, embeddings):
            node["embedding"] = emb.tolist()

        logger.info("Embeddings added to all nodes.")
