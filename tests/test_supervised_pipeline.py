"""
SIH26146 — Supervised ML Benchmark & Investigation Trace Test Suite
"""

import os
import json
import pickle
import pytest
import numpy as np

MODELS_DIR = r"c:\Users\apeksha\OneDrive\Documents\GitHub\Bitcoin-transaction\models"

def test_1_supervised_artifacts_exist():
    """Verify supervised model artifacts exist for Elliptic v1 and Elliptic v2."""
    for dataset in ['elliptic_v1', 'elliptic_v2']:
        base = os.path.join(MODELS_DIR, dataset)
        assert os.path.exists(os.path.join(base, "logistic_regression.pkl"))
        assert os.path.exists(os.path.join(base, "random_forest.pkl"))
        assert os.path.exists(os.path.join(base, "scaler_supervised.pkl"))
        assert os.path.exists(os.path.join(base, "supervised_evaluation_report.json"))
        assert os.path.exists(os.path.join(base, "final_ml_comparison.json"))

def test_2_supervised_metrics_validity():
    """Verify supervised benchmarks achieve valid ROC-AUC and PR-AUC scores."""
    for dataset in ['elliptic_v1', 'elliptic_v2']:
        comp_path = os.path.join(MODELS_DIR, dataset, "final_ml_comparison.json")
        with open(comp_path) as f:
            data = json.load(f)
        
        benchmarks = data.get("supervised_classification_benchmarks", {})
        lr = benchmarks.get("logistic_regression", {})
        rf = benchmarks.get("random_forest", {})

        assert "roc_auc" in lr and "pr_auc" in lr
        assert "roc_auc" in rf and "pr_auc" in rf

        assert 0.0 <= lr["roc_auc"] <= 1.0
        assert 0.0 <= rf["roc_auc"] <= 1.0
        assert rf["roc_auc"] > 0.70  # Random Forest benchmark sanity check

def test_3_offline_supervised_inference():
    """Verify saved Logistic Regression and Random Forest pkl models can generate predictions offline."""
    for dataset in ['elliptic_v1', 'elliptic_v2']:
        base = os.path.join(MODELS_DIR, dataset)
        with open(os.path.join(base, "logistic_regression.pkl"), 'rb') as f:
            lr_model = pickle.load(f)
        with open(os.path.join(base, "random_forest.pkl"), 'rb') as f:
            rf_model = pickle.load(f)
        with open(os.path.join(base, "scaler_supervised.pkl"), 'rb') as f:
            scaler = pickle.load(f)

        n_features = scaler.n_features_in_
        dummy_x = np.random.randn(5, n_features)
        dummy_scaled = scaler.transform(dummy_x)

        lr_preds = lr_model.predict(dummy_scaled)
        rf_preds = rf_model.predict(dummy_scaled)

        assert len(lr_preds) == 5
        assert len(rf_preds) == 5

def test_4_investigation_trace_integrity():
    """Verify pipeline service returns complete investigation trace provenance."""
    from backend.services import PipelineService
    service = PipelineService()
    trace = service.get_investigation_trace("tx_test_101")

    assert "investigation_tx_id" in trace
    assert "provenance_trace" in trace
    prov = trace["provenance_trace"]

    assert "1_network_layer_observation" in prov
    assert "2_transaction_layer" in prov
    assert "6_ml_model_signals" in prov
    assert "8_composite_risk_score" in prov
