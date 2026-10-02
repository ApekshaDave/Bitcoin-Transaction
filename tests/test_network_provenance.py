import pytest
import os
import sys
from fastapi.testclient import TestClient

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app, pipeline_service

client = TestClient(app)

def test_sih_synthetic_network_provenance():
    """Verify SIH Synthetic dataset exposes synthetic network data source."""
    pipeline_service.generate_and_ingest_data()
    res = client.get("/api/v1/network/observations?dataset=synthetic")
    assert res.status_code == 200
    data = res.json()
    assert data["dataset_source"] == "synthetic"
    assert data["network_data_source"] == "synthetic"
    assert data["network_data_provenance"] == "project_generated"
    assert data["geo_source"] == "synthetic"
    assert data["asn_source"] == "synthetic"
    assert isinstance(data["observations"], list)
    if data["observations"]:
        obs = data["observations"][0]
        assert obs["network_data_source"] == "synthetic"
        assert obs["network_data_provenance"] == "project_generated"

def test_elliptic_v1_network_provenance():
    """Verify Elliptic v1 network observations expose project-generated simulation provenance."""
    pipeline_service.load_elliptic_dataset(dataset_type="elliptic_v1", time_step_limit=2, max_txs=20)
    res = client.get("/api/v1/network/observations?dataset=elliptic_v1")
    assert res.status_code == 200
    data = res.json()
    assert data["dataset_source"] == "elliptic_v1"
    assert data["network_data_source"] == "synthetic"
    assert data["network_data_provenance"] == "project_generated"
    assert data["network_data_scope"] == "synthetic_network_simulation"
    assert isinstance(data["observations"], list)
    assert len(data["observations"]) > 0

    # Verify correlated TXIDs match valid Elliptic v1 transactions
    tx_res = client.get("/api/v1/transactions?dataset=elliptic_v1&limit=50")
    valid_txids = set(t["txid"] for t in tx_res.json())
    for obs in data["observations"]:
        assert obs["txid"] in valid_txids

def test_elliptic_v2_network_provenance():
    """Verify Elliptic++ v2 network observations expose project-generated simulation provenance."""
    pipeline_service.load_elliptic_dataset(dataset_type="elliptic_v2", time_step_limit=2, max_txs=20)
    res = client.get("/api/v1/network/observations?dataset=elliptic_v2")
    assert res.status_code == 200
    data = res.json()
    assert data["dataset_source"] == "elliptic_v2"
    assert data["network_data_source"] == "synthetic"
    assert data["network_data_provenance"] == "project_generated"
    assert data["network_data_scope"] == "synthetic_network_simulation"
    assert isinstance(data["observations"], list)

def test_dataset_switching_clears_stale_provenance():
    """Verify switching from Synthetic -> Elliptic v1 -> Synthetic updates provenance dynamically."""
    pipeline_service.generate_and_ingest_data()
    res1 = client.get("/api/v1/network/observations?dataset=synthetic")
    assert res1.json()["dataset_source"] == "synthetic"

    pipeline_service.load_elliptic_dataset(dataset_type="elliptic_v1", time_step_limit=2, max_txs=20)
    res2 = client.get("/api/v1/network/observations?dataset=elliptic_v1")
    assert res2.json()["dataset_source"] == "elliptic_v1"

    pipeline_service.generate_and_ingest_data()
    res3 = client.get("/api/v1/network/observations?dataset=synthetic")
    assert res3.json()["dataset_source"] == "synthetic"
