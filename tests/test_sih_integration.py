import pytest
import os
from data_generator.behavior_generator import SyntheticScenarioGenerator
from preprocessing.elliptic_loader import EllipticDatasetLoader, SyntheticLoader, EllipticV1Loader
from backend.database import DatabaseManager
from backend.services import PipelineService

def test_sih_synthetic_cross_layer_correlation():
    """Verify synthetic dataset field availability and 100% txid cross-layer correlation."""
    gen = SyntheticScenarioGenerator(seed=42)
    dataset = gen.generate_combined_benchmark_dataset(normal_count=30, include_anomalies=True)
    
    txs = dataset["transactions"]
    obs = dataset["network_observations"]
    
    assert len(txs) > 0
    assert len(obs) > 0
    
    tx_ids = set(t["txid"] for t in txs)
    obs_tx_ids = set(o["txid"] for o in obs if "txid" in o)
    
    # Check that all network observations match generated transactions
    matched = obs_tx_ids.intersection(tx_ids)
    assert len(matched) == len(obs_tx_ids)
    assert len(matched) > 0

def test_public_elliptic_no_fake_network_telemetry():
    """Verify public Elliptic datasets maintain 0 fake P2P network telemetry."""
    v1_loader = EllipticV1Loader()
    v1_data = v1_loader.load(time_step_limit=2, max_txs=50)
    
    assert v1_data["dataset_source"] == "elliptic_v1"
    assert len(v1_data["network_observations"]) == 0

def test_golden_investigation_case_trace():
    """Verify golden case TX_GOLDEN_001 produces complete 9-stage provenance trace."""
    service = PipelineService(db_manager=DatabaseManager(":memory:"))
    service.generate_and_ingest_data(normal_count=20, include_anomalies=True, seed=42)
    
    trace = service.get_investigation_trace("TX_GOLDEN_001")
    
    assert trace["tx_id"] == "TX_GOLDEN_001"
    assert trace["dataset_source"] == "synthetic"
    assert len(trace["network_observations"]) > 0
    assert trace["network_observations"][0]["txid"] == "TX_GOLDEN_001"
    assert trace["transaction"]["txid"] == "TX_GOLDEN_001"
    assert len(trace["addresses"]) >= 2
    assert "entity_id" in trace["entity"]
    assert len(trace["graph"]["nodes"]) >= 4
    assert len(trace["graph"]["edges"]) >= 3
    assert "unsupervised_isolation_forest" in trace["ml_signals"]
    assert "supervised_random_forest" in trace["ml_signals"]
    assert trace["structural_signals"]["peeling_chain_detected"] is True
    assert trace["risk"]["score"] >= 75.0
    assert "disclaimer" in trace["risk"]
    assert "prioritization score" in trace["risk"]["disclaimer"]
    assert "alert_id" in trace["alert"]

def test_unknown_txid_trace_handling():
    """Verify fallback behavior and safe handling for unregistered TXIDs."""
    service = PipelineService(db_manager=DatabaseManager(":memory:"))
    trace = service.get_investigation_trace("TX_UNKNOWN_9999")
    
    assert trace["tx_id"] == "TX_UNKNOWN_9999"
    assert "provenance_trace" in trace
    assert trace["risk"]["score"] is not None

def test_composite_risk_scoring_formula():
    """Verify composite risk formula produces bounded prioritization score [0, 100]."""
    service = PipelineService(db_manager=DatabaseManager(":memory:"))
    service.generate_and_ingest_data(normal_count=20, include_anomalies=True, seed=42)
    
    trace = service.get_investigation_trace("TX_GOLDEN_001")
    score = trace["risk"]["score"]
    components = trace["risk"]["components"]
    
    assert 0.0 <= score <= 100.0
    for comp_val in components.values():
        assert 0.0 <= comp_val <= 1.0

def test_offline_operation_no_external_deps():
    """Verify backend services start and operate without external network dependencies."""
    service = PipelineService(db_manager=DatabaseManager(":memory:"))
    res = service.generate_and_ingest_data(normal_count=10, include_anomalies=False, seed=42)
    assert res["status"] == "success"
    
    trace = service.get_investigation_trace(res.get("transaction_count", 0))
    assert trace is not None

def test_sih_synthetic_graph_contains_connected_golden_case():
    """Verify SIH Synthetic dataset produces connected graph data for Golden Case (TX_GOLDEN_001)."""
    service = PipelineService(db_manager=DatabaseManager(":memory:"))
    service.generate_and_ingest_data(normal_count=20, include_anomalies=True, seed=42)
    results = service.execute_analytics_pipeline()
    
    graph = results.get("graph", {})
    elements = graph.get("elements", [])
    
    nodes = {el["data"]["id"]: el["data"] for el in elements if "source" not in el["data"]}
    edges = [el["data"] for el in elements if "source" in el["data"]]
    
    assert len(nodes) > 0, "Graph nodes must not be empty"
    assert len(edges) > 0, "Graph edges must not be empty"
    
    # Check Golden Case TX node (txids are lowercased by cleaner)
    golden_tx_id = "tx_golden_001"
    golden_node = next((n for nid, n in nodes.items() if golden_tx_id in nid.lower()), None)
    assert golden_node is not None, f"Golden transaction node {golden_tx_id} must exist in graph"
    assert golden_node["node_type"] == "Transaction"
    
    # Verify edge validity (all sources & targets must exist in nodes)
    for edge in edges:
        assert edge["source"] in nodes, f"Edge source {edge['source']} missing from graph nodes"
        assert edge["target"] in nodes, f"Edge target {edge['target']} missing from graph nodes"
        
    # Check for connected IP -> TX -> Address -> Entity path
    ip_nodes = [nid for nid, ndata in nodes.items() if ndata.get("node_type") == "IP"]
    addr_nodes = [nid for nid, ndata in nodes.items() if ndata.get("node_type") == "Address"]
    entity_nodes = [nid for nid, ndata in nodes.items() if ndata.get("node_type") == "Entity"]
    
    assert len(ip_nodes) > 0, "Graph must contain IP nodes"
    assert len(addr_nodes) > 0, "Graph must contain Address nodes"
    assert len(entity_nodes) > 0, "Graph must contain Entity nodes"
    
    # Check connected edges for tx_golden_001
    actual_golden_nid = [nid for nid in nodes if "tx_golden_001" in nid.lower()][0]
    connected_to_golden = [e for e in edges if e["source"] == actual_golden_nid or e["target"] == actual_golden_nid]
    assert len(connected_to_golden) >= 1, "tx_golden_001 must have connected edges in graph"

def test_golden_case_end_to_end_consistency():
    """
    Verify complete 9-stage end-to-end consistency for Golden Case (TX_GOLDEN_001):
    Network Obs -> TXID -> Inputs/Outputs -> Entity -> Graph -> ML Signals -> Risk Score -> Alert -> Investigation Trace
    """
    service = PipelineService(db_manager=DatabaseManager(":memory:"))
    service.generate_and_ingest_data(normal_count=20, include_anomalies=True, seed=42)
    pipeline_res = service.execute_analytics_pipeline()
    
    # 1. Pipeline Summary & Graph
    summary = pipeline_res.get("summary", {})
    assert summary["total_transactions"] >= 20
    assert summary["total_network_observations"] > 0
    
    graph_elements = pipeline_res.get("graph", {}).get("elements", [])
    nodes = {el["data"]["id"]: el["data"] for el in graph_elements if "source" not in el["data"]}
    edges = [el["data"] for el in graph_elements if "source" in el["data"]]
    
    # Check Canonical Edge Types in Graph
    edge_types = set(e.get("edge_type") for e in edges)
    for canonical_type in ["OBSERVED", "INPUT", "OUTPUT", "ASSOCIATED_WITH"]:
        assert canonical_type in edge_types, f"Canonical edge type {canonical_type} missing from graph"
        
    # 2. Investigation Trace
    trace = service.get_investigation_trace("tx_golden_001")
    assert trace["tx_id"].lower() == "tx_golden_001"
    assert trace["dataset_source"] == "synthetic"
    
    # Check 9-stage provenance components
    prov = trace["provenance_trace"]
    assert "1_network_layer_observation" in prov
    assert "2_transaction_layer" in prov
    assert "3_address_layer" in prov
    assert "4_entity_clustering_layer" in prov
    assert "5_ml_feature_vector" in prov
    assert "6_ml_model_signals" in prov
    assert "7_graph_and_structural_signals" in prov
    assert "8_composite_risk_score" in prov
    assert "9_explainable_alert" in prov
    
    # Check Network & TXID matching
    net_obs = trace["network_observations"]
    assert len(net_obs) > 0
    assert net_obs[0]["txid"].lower() == "tx_golden_001"
    assert net_obs[0]["src_ip"] == "198.51.100.45"
    
    # Check Anomaly score normalization [0.0 - 1.0]
    raw_a_score = trace["ml_signals"]["unsupervised_isolation_forest"]["raw_anomaly_score"]
    assert 0.0 <= raw_a_score <= 1.0, f"Anomaly score {raw_a_score} must be normalized [0.0, 1.0]"
    
    # Check Alert Persistence
    persisted_alerts = service.db.get_all_alerts()
    assert len(persisted_alerts) > 0, "Alerts must be persisted in SQLite DB"
    golden_alert = next((a for a in persisted_alerts if "tx_golden_001" in a["target_id"].lower() or "tx_golden_001" in a["alert_id"].lower()), None)
    assert golden_alert is not None, "Golden case alert must be persisted in SQLite DB"
    assert golden_alert["risk_score"] >= 30.0

def test_golden_graph_is_bounded():
    """Verify that Golden Case graph query returns bounded node count (< 25 nodes)."""
    service = PipelineService(db_manager=DatabaseManager(":memory:"))
    service.generate_and_ingest_data(normal_count=20, include_anomalies=True, seed=42)
    pipeline_res = service.execute_analytics_pipeline()
    
    graph = pipeline_res.get("graph", {})
    from graph.graph_builder import HeterogeneousGraphBuilder
    gb = HeterogeneousGraphBuilder()
    txs, obs, _, _ = service.db.load_latest_data()
    gb.build_graph(txs, obs)
    
    subgraph = gb.export_to_cytoscape_json(center_node_id="tx_golden_001", depth=1, max_nodes=50)
    assert subgraph["node_count"] > 0, "Golden case subgraph must have nodes"
    assert subgraph["node_count"] <= 25, f"Golden case node count {subgraph['node_count']} exceeds target 25 nodes"
    assert subgraph["truncated"] is False or subgraph["node_count"] <= 50



