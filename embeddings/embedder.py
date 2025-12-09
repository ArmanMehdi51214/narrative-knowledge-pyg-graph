# embeddings/embedder.py

"""
Embedding generator using SentenceTransformers (MiniLM-L6-v2).
Nodes are Node dataclass objects — this version handles objects safely.
"""

from __future__ import annotations
import logging
from typing import List
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingGenerator:

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        logger.info("Loading embedding model: %s", model_name)
        self.model = SentenceTransformer(model_name)

    # --------------------------------------------------------
    # Extract best available text for embedding
    # --------------------------------------------------------
    def _get_text_for_node(self, node) -> str:
        """
        Node is a dataclass (object), not a dict.
        Prefer summary → description → label.
        """
        if node.summary and node.summary.strip():
            return node.summary

        if node.description and node.description.strip():
            return node.description

        return node.label or "unknown"

    # --------------------------------------------------------
    # Generate embeddings for all Node objects
    # --------------------------------------------------------
    def embed_nodes(self, nodes: List) -> None:
        logger.info("Preparing text for %d nodes...", len(nodes))

        texts = [self._get_text_for_node(node) for node in nodes]

        logger.info("Computing embeddings... this may take a moment.")
        embeddings = self.model.encode(texts, show_progress_bar=True)

        logger.info("Assigning embeddings to Node objects.")
        for node, emb in zip(nodes, embeddings):
            node.embedding = emb.tolist()

        logger.info("Embeddings added to all nodes.")
