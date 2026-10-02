import pytest
import pandas as pd
from data_generator.behavior_generator import SyntheticScenarioGenerator
from preprocessing.transaction_cleaner import TransactionCleaner
from preprocessing.network_cleaner import NetworkCleaner
from preprocessing.cross_layer_correlator import CrossLayerCorrelator
from preprocessing.feature_builder import FeatureBuilder
from graph.graph_builder import HeterogeneousGraphBuilder
from ml.clustering.entity_clusterer import EntityClusterer
from ml.anomaly_detection.anomaly_detector import AnomalyDetector
from ml.peeling_detection.peeling_classifier import PeelingChainDetector
from ml.mixing_detection.mixing_classifier import MixingPatternDetector
from ml.risk_scoring.risk_engine import RiskEngine
from backend.database import DatabaseManager
from backend.services import PipelineService

def test_synthetic_data_generation():
    gen = SyntheticScenarioGenerator(seed=42)
    dataset = gen.generate_combined_benchmark_dataset(normal_count=20, include_anomalies=True)
    
    assert len(dataset["transactions"]) > 20
    assert len(dataset["network_observations"]) > 20
    assert "peeling_chain" in dataset["metadata"]["scenario_distribution"]

    # Verify input prev_txid schema
    txs = dataset["transactions"]
    sample_tx = txs[0]
    assert "inputs" in sample_tx
    assert "outputs" in sample_tx
    assert "prev_txid" in sample_tx["inputs"][0]

def test_cross_layer_correlation():
    gen = SyntheticScenarioGenerator(seed=42)
    dataset = gen.generate_combined_benchmark_dataset(normal_count=10, include_anomalies=True)
    txs = TransactionCleaner.clean_transactions(dataset["transactions"])
    obs = NetworkCleaner.clean_observations(dataset["network_observations"])

    correlator = CrossLayerCorrelator(txs, obs)
    summary = correlator.get_correlation_summary()
    
    assert summary["total_correlated_transactions"] > 0
    assert summary["total_unique_ips"] > 0

def test_graph_construction():
    gen = SyntheticScenarioGenerator(seed=42)
    dataset = gen.generate_combined_benchmark_dataset(normal_count=10, include_anomalies=True)
    txs = TransactionCleaner.clean_transactions(dataset["transactions"])
    obs = NetworkCleaner.clean_observations(dataset["network_observations"])

    builder = HeterogeneousGraphBuilder()
    graph = builder.build_graph(txs, obs)
    
    assert graph.number_of_nodes() > 0
    assert graph.number_of_edges() > 0

    cy_json = builder.export_to_cytoscape_json()
    assert "elements" in cy_json
    assert len(cy_json["elements"]) > 0

def test_ml_pipeline_and_risk_engine():
    service = PipelineService(db_manager=DatabaseManager(":memory:"))
    gen_res = service.generate_and_ingest_data(normal_count=20, include_anomalies=True, seed=42)
    assert gen_res["status"] == "success"

    pipeline_res = service.execute_analytics_pipeline()
    assert pipeline_res["status"] == "completed"
    assert "summary" in pipeline_res
    assert pipeline_res["summary"]["total_transactions"] > 0
    assert "evaluation_metrics" in pipeline_res

def test_elliptic_v1_pipeline_loading():
    service = PipelineService(db_manager=DatabaseManager(":memory:"))
    res = service.load_elliptic_dataset("elliptic_v1", time_step_limit=2, max_txs=50)
    assert res["status"] == "success"
    assert res["dataset_source"] == "elliptic_v1"
    assert res["summary"]["total_transactions"] > 0
    assert "evaluation_metrics" in res
    assert "classification" in res["evaluation_metrics"]

def test_elliptic_v2_pipeline_loading():
    service = PipelineService(db_manager=DatabaseManager(":memory:"))
    res = service.load_elliptic_dataset("elliptic_v2", time_step_limit=2, max_txs=50)
    assert res["status"] == "success"
    assert res["dataset_source"] == "elliptic_v2"
    assert res["summary"]["total_wallets"] > 0
    assert "graph" in res

def test_label_isolation_no_leakage():
    """Verify that class_label feature is excluded from unsupervised model feature matrices"""
    from preprocessing.elliptic_loader import EllipticDatasetLoader
    from ml.model_trainer import ModelTrainer

    loader = EllipticDatasetLoader.get_loader("elliptic_v1", time_step_limit=2, max_txs=50)
    data = loader.load_data()
    txs = data["transactions"]

    trainer = ModelTrainer()
    train_res = trainer.train_and_evaluate(txs, dataset_source="elliptic_v1")
    
    assert "evaluation_metrics" in train_res
    assert train_res["evaluation_metrics"]["classification"]["evaluated_samples"] > 0

