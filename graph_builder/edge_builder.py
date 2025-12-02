# Create graph edges from Wikidata relations (instance of, subclass of, based on, influenced by, etc.)
# graph_builder/edge_builder.py

import logging
from typing import List, Dict, Optional

from wd_api.wikidata_client import WikidataClient


class EdgeBuilder:
    """
    Builds semantic edges between nodes using Wikidata relationships.

    Uses a mapping of Wikidata property IDs → normalized ML relation names.
    """

    # Wikidata property → semantic relation name
    RELATION_MAP = {
        "P31": "is_a",             # instance of
        "P279": "is_a",            # subclass of
        "P737": "inspired_by",     # influenced by
        "P144": "based_on",        # based on
        "P921": "associated_with", # main subject
    }

    def __init__(self):
        self.wd = WikidataClient()
        self.logger = logging.getLogger(self.__class__.__name__)

    # -------------------------------------------------------------------
    # Public method: Build all edges for your set of node IDs
    # -------------------------------------------------------------------
    def build_edges(self, node_ids: List[str]) -> List[Dict]:
        """
        Build edges for all entities using pre-defined Wikidata relations.

        Parameters
        ----------
        node_ids : List[str]
            List of QIDs representing nodes already included in the graph.

        Returns
        -------
        List[Dict]
            List of edges in normalized graph format.
        """
        all_edges = []

        for property_id, relation_name in self.RELATION_MAP.items():
            edges = self._fetch_edges_for_property(
                node_ids=node_ids,
                property_id=property_id,
                relation_name=relation_name,
            )
            all_edges.extend(edges)

        self.logger.info(f"Total edges built: {len(all_edges)}")
        return all_edges

    # -------------------------------------------------------------------
    # Fetch edges for a single Wikidata property (P31, P279, etc.)
    # -------------------------------------------------------------------
    def _fetch_edges_for_property(
        self,
        node_ids: List[str],
        property_id: str,
        relation_name: str
    ) -> List[Dict]:
        """
        Query Wikidata for subject → object relations using a specific property.
        Only edges whose target is also in node_ids are kept (clean graph).
        """

        if not node_ids:
            return []

        qids_str = " ".join(f"wd:{qid}" for qid in node_ids)

        query = f"""
        SELECT ?subject ?object WHERE {{
            VALUES ?subject {{ {qids_str} }}
            ?subject wdt:{property_id} ?object .
        }}
        """

        try:
            data = self.wd.run_sparql(query)
        except Exception as e:
            self.logger.error(f"SPARQL request failed for {property_id}: {e}")
            return []

        results = data.get("results", {}).get("bindings", [])
        edges = []

        for row in results:
            try:
                source_qid = row["subject"]["value"].split("/")[-1]
                target_qid = row["object"]["value"].split("/")[-1]

                # Only keep edges where target is also a node in the graph
                if target_qid not in node_ids:
                    continue

                edge = {
                    "source": source_qid,
                    "target": target_qid,
                    "relation": relation_name,
                    "weight": 1.0,
                    "detection_method": f"wikidata:{property_id}",
                }
                edges.append(edge)

            except Exception as e:
                self.logger.error(f"Failed to parse row {row}: {e}")

        self.logger.info(f"Edges for {property_id} ({relation_name}): {len(edges)}")
        return edges
