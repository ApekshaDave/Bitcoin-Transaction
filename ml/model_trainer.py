import os
import json
import pickle
import datetime
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, silhouette_score

MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))

class ModelTrainer:
    """
    Trains, evaluates, and saves real ML models (Isolation Forest & DBSCAN) for:
    - synthetic dataset
    - elliptic_v1 dataset
    - elliptic_v2 dataset

    Strictly separates ground-truth class_labels from unsupervised model input features,
    and implements temporal splitting to prevent temporal leakage.
    """

    def train_and_evaluate(self, transactions: List[Dict[str, Any]], dataset_source: str = "elliptic_v1") -> Dict[str, Any]:
        """Convenience wrapper for testing model training with list of transactions."""
        dataset_dict = {
            "dataset_source": dataset_source,
            "transactions": transactions,
            "edges": [],
            "network_observations": [],
            "wallets": []
        }
        return self.train_and_save_pipeline(dataset_dict)

    def train_and_save_pipeline(self, dataset_dict: Dict[str, Any], save_dir: Optional[str] = None) -> Dict[str, Any]:
        source = dataset_dict.get("dataset_source", "synthetic")
        target_dir = save_dir or os.path.join(MODELS_DIR, source)
        os.makedirs(target_dir, exist_ok=True)

        transactions = dataset_dict.get("transactions", [])
        if not transactions:
            raise ValueError(f"No transactions found in dataset dict for {source}")

        # 1. Build Feature Matrix X and Ground Truth Labels y
        X_df, y_series, time_steps = self._extract_features_and_labels(dataset_dict)

        feature_names = list(X_df.columns)
        if len(feature_names) == 0:
            raise ValueError(f"No valid numeric feature columns extracted for dataset {source}")

        # 2. Temporal Leakage Prevention (Split by time steps if temporal data exists)
        max_ts = max(time_steps) if time_steps else 1
        min_ts = min(time_steps) if time_steps else 1

        if max_ts > min_ts:
            split_ts = int(min_ts + (max_ts - min_ts) * 0.7)
            train_mask = [ts <= split_ts for ts in time_steps]
            test_mask = [ts > split_ts for ts in time_steps]
        else:
            split_ts = max_ts
            train_mask = [True] * len(X_df)
            test_mask = [True] * len(X_df)

        X_train = X_df[train_mask].values
        X_test = X_df[test_mask].values if any(test_mask) else X_train

        y_train = y_series[train_mask].values
        y_test = y_series[test_mask].values if any(test_mask) else y_train

        # 3. Fit StandardScaler & Transform
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test) if len(X_test) > 0 else X_train_scaled

        # 4. Train Isolation Forest (Unsupervised Anomaly Detector)
        iso_forest = IsolationForest(n_estimators=100, contamination=0.1, random_state=42)
        iso_forest.fit(X_train_scaled)

        # Predict anomaly scores (decision_function converted to 0..1 scale where 1 is high anomaly)
        raw_scores_test = -iso_forest.decision_function(X_test_scaled)
        min_s, max_s = raw_scores_test.min(), raw_scores_test.max()
        if max_s > min_s:
            norm_scores_test = (raw_scores_test - min_s) / (max_s - min_s)
        else:
            norm_scores_test = np.zeros_like(raw_scores_test)

        # 5. Train DBSCAN (Unsupervised Entity/Address Clustering)
        dbscan = DBSCAN(eps=0.5, min_samples=2)
        dbscan_labels_train = dbscan.fit_predict(X_train_scaled)

        # 6. Model Evaluation (Labels strictly for evaluation ONLY)
        # Filter evaluation samples to labeled classes (Class 1 Illicit vs Class 2 Licit, ignoring Class 3 Unknown)
        eval_mask = (y_test == 1) | (y_test == 2)
        if np.sum(eval_mask) > 0:
            y_eval_true = (y_test[eval_mask] == 1).astype(int)
            y_eval_scores = norm_scores_test[eval_mask]
            y_eval_pred = (y_eval_scores >= 0.5).astype(int)

            prec = float(precision_score(y_eval_true, y_eval_pred, zero_division=0))
            rec = float(recall_score(y_eval_true, y_eval_pred, zero_division=0))
            f1 = float(f1_score(y_eval_true, y_eval_pred, zero_division=0))
            try:
                auc_roc = float(roc_auc_score(y_eval_true, y_eval_scores))
            except Exception:
                auc_roc = 0.5
            try:
                auc_pr = float(average_precision_score(y_eval_true, y_eval_scores))
            except Exception:
                auc_pr = 0.0
        else:
            prec, rec, f1, auc_roc, auc_pr = 0.0, 0.0, 0.0, 0.5, 0.0

        # DBSCAN Clustering Evaluation
        n_clusters = int(len(set(dbscan_labels_train)) - (1 if -1 in dbscan_labels_train else 0))
        noise_ratio = float(np.sum(dbscan_labels_train == -1) / len(dbscan_labels_train)) if len(dbscan_labels_train) > 0 else 0.0
        sil_score = 0.0
        if n_clusters > 1 and len(X_train_scaled) <= 5000:
            try:
                sil_score = float(silhouette_score(X_train_scaled, dbscan_labels_train))
            except Exception:
                sil_score = 0.0

        def _clean_float(val: Any, default: float = 0.0) -> float:
            try:
                f_val = float(val)
                if np.isnan(f_val) or np.isinf(f_val):
                    return default
                return round(f_val, 4)
            except Exception:
                return default

        evaluation_metrics = {
            "classification": {
                "precision": _clean_float(prec),
                "recall": _clean_float(rec),
                "f1_score": _clean_float(f1),
                "roc_auc": _clean_float(auc_roc, 0.5),
                "pr_auc": _clean_float(auc_pr),
                "evaluated_samples": int(np.sum(eval_mask)),
                "label_note": "Evaluated strictly on Class 1 (Illicit) vs Class 2 (Licit), Class 3 (Unknown) excluded"
            },
            "clustering": {
                "num_clusters": n_clusters,
                "noise_percentage": _clean_float(noise_ratio * 100),
                "silhouette_score": _clean_float(sil_score)
            }
        }

        # 7. Save Model Artifacts
        with open(os.path.join(target_dir, "isolation_forest.pkl"), "wb") as f:
            pickle.dump(iso_forest, f)

        with open(os.path.join(target_dir, "scaler.pkl"), "wb") as f:
            pickle.dump(scaler, f)

        with open(os.path.join(target_dir, "dbscan.pkl"), "wb") as f:
            pickle.dump(dbscan, f)

        # Save feature schema
        feature_schema = {
            "dataset_source": source,
            "total_features": len(feature_names),
            "feature_names": feature_names,
            "scaling_method": "StandardScaler",
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "temporal_split_time_step": split_ts
        }
        with open(os.path.join(target_dir, "feature_schema.json"), "w") as f:
            json.dump(feature_schema, f, indent=2)

        # Save training metadata
        training_metadata = {
            "dataset_source": source,
            "trained_at": datetime.datetime.utcnow().isoformat() + "Z",
            "model_version": "1.0.0",
            "n_train_samples": len(X_train),
            "n_test_samples": len(X_test),
            "min_time_step": min_ts,
            "max_time_step": max_ts,
            "split_time_step": split_ts,
            "model_parameters": {
                "isolation_forest": {"n_estimators": 100, "contamination": 0.1, "random_state": 42},
                "dbscan": {"eps": 0.5, "min_samples": 2}
            }
        }
        with open(os.path.join(target_dir, "training_metadata.json"), "w") as f:
            json.dump(training_metadata, f, indent=2)

        with open(os.path.join(target_dir, "evaluation_metrics.json"), "w") as f:
            json.dump(evaluation_metrics, f, indent=2)

        return {
            "status": "success",
            "dataset_source": source,
            "save_dir": target_dir,
            "feature_count": len(feature_names),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "evaluation_metrics": evaluation_metrics
        }

    def _extract_features_and_labels(self, dataset_dict: Dict[str, Any]) -> Tuple[pd.DataFrame, pd.Series, List[int]]:
        """Extracts X (feature dataframe), y (ground truth labels), and time steps."""
        transactions = dataset_dict.get("transactions", [])
        feature_matrices = dataset_dict.get("feature_matrices", {})

        records = []
        labels = []
        time_steps = []

        for tx in transactions:
            txid = str(tx["txid"])
            ts = int(tx.get("time_step", 1))
            c_label = int(tx.get("class_label", 3))

            labels.append(c_label)
            time_steps.append(ts)

            if txid in feature_matrices:
                records.append(feature_matrices[txid])
            else:
                # Fallback to standard transaction numerical attributes
                records.append([
                    float(tx.get("fee", 0)),
                    float(tx.get("size", 250)),
                    float(tx.get("weight", 1000)),
                    float(tx.get("input_count", 1)),
                    float(tx.get("output_count", 2)),
                    float(tx.get("total_input_amount", 0)),
                    float(tx.get("total_output_amount", 0))
                ])

        feature_names = dataset_dict.get("feature_names")
        if not feature_names and records:
            feature_names = [f"feat_{i+1}" for i in range(len(records[0]))]

        X_df = pd.DataFrame(records, columns=feature_names)
        y_series = pd.Series(labels)

        return X_df, y_series, time_steps
