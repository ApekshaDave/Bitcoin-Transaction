import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any, Tuple

class EntityClusterer:
    """
    Entity Clustering Engine using DBSCAN.
    Operates on a numerical feature matrix generated from address-level behavioral, 
    temporal, financial, and graph features (including common-input heuristic signals).
    
    Generates inferred entity_id cluster mappings for potential related address clusters.
    """
    def __init__(self, eps: float = 0.5, min_samples: int = 2):
        self.eps = eps
        self.min_samples = min_samples
        self.scaler = StandardScaler()
        self.model = DBSCAN(eps=self.eps, min_samples=self.min_samples)

    def fit_predict_clusters(self, address_df: pd.DataFrame) -> Tuple[Dict[str, str], pd.DataFrame]:
        """
        Fits DBSCAN on normalized address numerical feature matrix.
        
        Returns:
            - Dict[address, entity_id] mapping
            - Address DataFrame enriched with 'entity_id' and 'cluster_label'
        """
        if address_df.empty or len(address_df) < 2:
            return {}, address_df

        feature_cols = [
            "tx_count", "sent_amount", "recv_amount", "total_amount",
            "common_input_signal", "unique_counterparties", "unique_ips",
            "unique_asns", "unique_countries", "avg_time_delta"
        ]
        
        # Include graph features if present
        for optional_col in ["pagerank", "graph_degree"]:
            if optional_col in address_df.columns:
                feature_cols.append(optional_col)

        X = address_df[feature_cols].copy()
        X_scaled = self.scaler.fit_transform(X)

        labels = self.model.fit_predict(X_scaled)
        address_df = address_df.copy()
        address_df["cluster_label"] = labels

        # Map integer labels to readable entity_ids (e.g., entity_cluster_0, unclustered_address)
        entity_map = {}
        entity_ids = []
        for idx, row in address_df.iterrows():
            addr = row["address"]
            lbl = row["cluster_label"]
            if lbl == -1:
                e_id = f"entity_unclustered_{addr[:6]}"
            else:
                e_id = f"entity_cluster_{lbl:03d}"
            entity_map[addr] = e_id
            entity_ids.append(e_id)

        address_df["entity_id"] = entity_ids
        return entity_map, address_df
