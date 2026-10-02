import numpy as np
import pandas as pd
from sklearn.metrics import (
    silhouette_score, davies_bouldin_score,
    precision_score, recall_score, f1_score, precision_recall_curve, auc
)
from typing import Dict, Any, List

class ModelEvaluator:
    """
    Model Evaluation Engine for SIH26146.
    Computes task-specific ML metrics across:
    - Entity Clustering (Silhouette, Davies-Bouldin)
    - Anomaly Detection (Precision@K, Recall@K, PR-AUC)
    - Peeling & Mixing Detection (Precision, Recall, F1, PR-AUC)
    - Risk Ranking Prioritization (Precision@K, Recall@K)
    """

    @staticmethod
    def evaluate_clustering(df: pd.DataFrame, feature_cols: List[str]) -> Dict[str, float]:
        """Evaluates clustering performance using Silhouette and Davies-Bouldin scores."""
        if df.empty or "cluster_label" not in df.columns:
            return {"silhouette_score": 0.0, "davies_bouldin_index": 0.0}

        valid_df = df[df["cluster_label"] != -1]
        if len(valid_df) < 3 or len(valid_df["cluster_label"].unique()) < 2:
            return {"silhouette_score": 0.0, "davies_bouldin_index": 0.0}

        X = valid_df[feature_cols].fillna(0)
        labels = valid_df["cluster_label"]

        sil = float(silhouette_score(X, labels))
        db = float(davies_bouldin_score(X, labels))

        return {
            "silhouette_score": round(sil, 4),
            "davies_bouldin_index": round(db, 4)
        }

    @staticmethod
    def evaluate_classification(
        y_true: List[int], 
        y_pred: List[int], 
        y_scores: List[float] = None
    ) -> Dict[str, float]:
        """Evaluates binary classification tasks (Peeling/Mixing pattern detection)."""
        if len(y_true) == 0:
            return {"precision": 0.0, "recall": 0.0, "f1_score": 0.0, "pr_auc": 0.0}

        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))

        pr_auc_val = 0.0
        if y_scores is not None and len(y_scores) == len(y_true):
            p, r, _ = precision_recall_curve(y_true, y_scores)
            pr_auc_val = float(auc(r, p))

        return {
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "pr_auc": round(pr_auc_val, 4)
        }

    @staticmethod
    def evaluate_precision_at_k(
        y_true: List[int], 
        risk_scores: List[float], 
        k: int = 10
    ) -> Dict[str, float]:
        """Evaluates Risk Ranking Prioritization at Top-K."""
        if len(y_true) == 0 or len(risk_scores) != len(y_true):
            return {"precision_at_k": 0.0, "recall_at_k": 0.0}

        # Sort by risk score descending
        sorted_indices = np.argsort(risk_scores)[::-1]
        top_k_indices = sorted_indices[:min(k, len(sorted_indices))]

        top_k_true = [y_true[i] for i in top_k_indices]
        total_positives = sum(y_true)

        p_at_k = sum(top_k_true) / max(1, len(top_k_true))
        r_at_k = sum(top_k_true) / max(1, total_positives)

        return {
            "precision_at_k": round(p_at_k, 4),
            "recall_at_k": round(r_at_k, 4)
        }
