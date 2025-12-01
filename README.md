# narrative-knowledge-pyg-graph
Narrative Knowledge Graph Pipeline with PyTorch Geometric

This project implements a complete, end-to-end pipeline for constructing a large-scale Narrative Knowledge Graph using legal, structured data sources. The goal is to model narrative intelligence across folklore, science fiction, and video game mechanics by linking ancient storytelling motifs to modern conceptual structures.

The system replaces traditional web scraping with a fully compliant data-acquisition layer built on the Wikidata SPARQL API and the Wikipedia REST API. This approach provides stable, high-quality knowledge sources suitable for commercial and research applications.

The pipeline includes:

• A modular Wikidata client capable of extracting motif information, ATU folktale classifications, genre-specific concepts, and mechanical structures using configurable SPARQL queries.
• A Wikipedia enrichment module for retrieving introductory summaries used in downstream embedding generation.
• A graph builder that merges Wikidata entities with Wikipedia text, constructs semantic edges from Wikidata relations, and validates graph structure.
• An embedding layer using SentenceTransformer (MiniLM-L6-v2) to generate dense narrative feature vectors.
• A NetworkX validation stage to ensure structural consistency and remove orphaned nodes.
• A PyTorch Geometric conversion component that produces training-ready graph tensors, including node features, edge indices, and relation attributes.

The entire pipeline is designed to run from a single command with configurable query parameters, enabling the generation of domain-specific narrative graphs of varying scope. The output includes both a JSON dataset and a PyG graph object suitable for downstream GNN training and narrative reasoning research.
