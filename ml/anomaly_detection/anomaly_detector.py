import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Dict, Any

class AnomalyDetector:
    """
    Unsupervised Anomaly Detection Engine using Isolation Forest.
    Calculates normalized anomaly scores [0.0, 1.0] based on multi-dimensional
    financial, temporal, network, and graph features.
    """
    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            contamination=self.contamination, 
            random_state=self.random_state,
            n_estimators=100
        )

    def detect_transaction_anomalies(self, tx_df: pd.DataFrame) -> pd.DataFrame:
        """
        Detects anomalous transaction patterns.
        
        Returns tx_df enriched with 'anomaly_score' [0.0 - 1.0] and 'is_anomaly' flag.
        """
        if tx_df.empty or len(tx_df) < 3:
            tx_df["anomaly_score"] = 0.0
            tx_df["is_anomaly"] = 0
            return tx_df

        feature_cols = [
            "input_count", "output_count", "total_amount", "fee",
            "fee_ratio", "output_entropy", "time_delta", "unique_src_ips", "in_out_ratio"
        ]
        
        available_cols = [col for col in feature_cols if col in tx_df.columns]
        X = tx_df[available_cols].fillna(0).copy()
        X_scaled = self.scaler.fit_transform(X)

        # Isolation Forest decision_function returns negative for anomalies, positive for normal
        raw_scores = self.model.fit_predict(X_scaled)
        dec_scores = self.model.decision_function(X_scaled)

        # Invert and normalize decision scores to range [0.0, 1.0] where 1.0 = highly anomalous
        min_s, max_s = float(np.min(dec_scores)), float(np.max(dec_scores))
        if max_s > min_s:
            norm_scores = (max_s - dec_scores) / (max_s - min_s)
        else:
            norm_scores = np.zeros(len(dec_scores))

        tx_df = tx_df.copy()
        tx_df["anomaly_score"] = np.round(norm_scores, 4)
        tx_df["is_anomaly"] = np.where(raw_scores == -1, 1, 0)
        return tx_df
