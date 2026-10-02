import networkx as nx
import pandas as pd
from typing import Dict, Any

class GraphFeatureExtractor:
    """
    Computes structural topological metrics from the NetworkX heterogeneous graph:
    - Degree, In-Degree, Out-Degree
    - PageRank Centrality
    - Neighborhood diversity
    """
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def compute_all_graph_metrics(self) -> Dict[str, Dict[str, float]]:
        if self.graph.number_of_nodes() == 0:
            return {}

        pagerank = nx.pagerank(self.graph, alpha=0.85) if self.graph.number_of_nodes() > 1 else {n: 1.0 for n in self.graph.nodes()}
        in_degrees = dict(self.graph.in_degree())
        out_degrees = dict(self.graph.out_degree())

        metrics = {}
        for n in self.graph.nodes():
            metrics[n] = {
                "in_degree": float(in_degrees.get(n, 0)),
                "out_degree": float(out_degrees.get(n, 0)),
                "total_degree": float(in_degrees.get(n, 0) + out_degrees.get(n, 0)),
                "pagerank": round(float(pagerank.get(n, 0.0)), 6)
            }
        return metrics

    def enrich_feature_matrix_with_graph_metrics(self, address_df: pd.DataFrame) -> pd.DataFrame:
        """
        Enriches address-level feature DataFrame with graph topological metrics.
        """
        if address_df.empty:
            address_df["pagerank"] = 0.0
            address_df["graph_degree"] = 0.0
            return address_df

        metrics = self.compute_all_graph_metrics()

        pageranks = []
        degrees = []

        for addr in address_df["address"]:
            node_id = f"addr:{addr}"
            if node_id in metrics:
                pageranks.append(metrics[node_id]["pagerank"])
                degrees.append(metrics[node_id]["total_degree"])
            else:
                pageranks.append(0.0)
                degrees.append(0.0)

        address_df["pagerank"] = pageranks
        address_df["graph_degree"] = degrees
        return address_df
