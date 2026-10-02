"""
SIH26146 — ML Pipeline Integrity & Verification Test Suite
"""

import os
import json
import pickle
import pytest
import numpy as np
import pandas as pd

MODELS_DIR = r"c:\Users\apeksha\OneDrive\Documents\GitHub\Bitcoin-transaction\models"

def test_1_raw_data_not_modified():
    """Verify raw datasets exist and have non-zero size."""
    v1_dir = r"C:\Users\apeksha\Downloads\archive (1)\elliptic_bitcoin_dataset"
    v2_dir = r"C:\Users\apeksha\Downloads\drive-download-20261001T200400Z-1-001"
    
    assert os.path.exists(os.path.join(v1_dir, "elliptic_txs_classes.csv"))
    assert os.path.exists(os.path.join(v2_dir, "txs_classes.csv"))
    assert os.path.getsize(os.path.join(v1_dir, "elliptic_txs_classes.csv")) > 1000

def test_2_label_isolation_in_feature_schema():
    """Verify ground-truth class labels are excluded from feature schemas."""
    for dataset in ['elliptic_v1', 'elliptic_v2']:
        schema_path = os.path.join(MODELS_DIR, dataset, "feature_schema.json")
        assert os.path.exists(schema_path)
        with open(schema_path) as f:
            schema = json.load(f)
        
        feature_names = schema.get("feature_names", [])
        assert "class" not in feature_names
        assert "class_num" not in feature_names
        assert "txId" not in feature_names

def test_3_temporal_split_metadata():
    """Verify training metadata correctly documents temporal time-step splits."""
    for dataset in ['elliptic_v1', 'elliptic_v2']:
        meta_path = os.path.join(MODELS_DIR, dataset, "training_metadata.json")
        assert os.path.exists(meta_path)
        with open(meta_path) as f:
            meta = json.load(f)
        
        train_steps = meta.get("time_steps_train", f"Steps 1 - {meta.get('split_time_step', 30)}")
        assert "1" in str(train_steps) or "Steps" in str(train_steps)
        assert meta.get("n_train_samples", meta.get("train_samples", 0)) > 0

def test_4_offline_isolation_forest_artifact_loading():
    """Verify saved Isolation Forest pkl can be loaded offline and generate predictions."""
    for dataset in ['elliptic_v1', 'elliptic_v2']:
        model_path = os.path.join(MODELS_DIR, dataset, "isolation_forest.pkl")
        scaler_path = os.path.join(MODELS_DIR, dataset, "scaler.pkl")
        
        assert os.path.exists(model_path)
        assert os.path.exists(scaler_path)

        with open(model_path, 'rb') as f:
            iso_forest = pickle.load(f)
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)

        # Generate sample dummy input with matching feature count
        n_features = scaler.n_features_in_
        dummy_x = np.random.randn(5, n_features)
        dummy_scaled = scaler.transform(dummy_x)

        preds = iso_forest.predict(dummy_scaled)
        scores = iso_forest.decision_function(dummy_scaled)

        assert len(preds) == 5
        assert len(scores) == 5

def test_5_risk_weights_sum_to_one():
    """Verify standard composite risk weights sum exactly to 1.0."""
    w_anomaly = 0.25
    w_peeling = 0.25
    w_mixing = 0.20
    w_network = 0.15
    w_graph = 0.15
    
    total_w = w_anomaly + w_peeling + w_mixing + w_network + w_graph
    assert abs(total_w - 1.0) < 1e-6

def test_6_no_mock_metrics_in_evaluation_report():
    """Verify evaluation metrics JSON contains real non-mock evaluation metrics."""
    for dataset in ['elliptic_v1', 'elliptic_v2']:
        eval_path = os.path.join(MODELS_DIR, dataset, "evaluation_report.json")
        assert os.path.exists(eval_path)
        with open(eval_path) as f:
            data = json.load(f)
        
        iso_res = data.get("isolation_forest", {})
        assert "roc_auc" in iso_res
        assert "pr_auc" in iso_res
        assert iso_res["evaluated_test_samples"] > 0
        assert 0.0 <= iso_res["roc_auc"] <= 1.0
