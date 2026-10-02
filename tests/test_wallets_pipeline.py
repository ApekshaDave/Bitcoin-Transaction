import pytest
from fastapi.testclient import TestClient
from backend.main import app, pipeline_service

client = TestClient(app)

def test_elliptic_v1_wallets_not_provided():
    """
    Verifies that Elliptic v1 returns status NOT_PROVIDED and N/A wallet metrics,
    preserving scientific correctness for transaction-only benchmark datasets.
    """
    # 1. Test GET /api/v1/wallets?dataset=elliptic_v1
    res = client.get("/api/v1/wallets?dataset=elliptic_v1")
    assert res.status_code == 200
    data = res.json()
    assert data["dataset_source"] == "elliptic_v1"
    assert data["status"] == "NOT_PROVIDED"
    assert data["total_count"] == "N/A"
    assert data["wallets"] == []
    assert "N/A" in data["message"]

    # 2. Test GET /api/v1/overview/kpis?dataset=elliptic_v1
    kpi_res = client.get("/api/v1/overview/kpis?dataset=elliptic_v1")
    assert kpi_res.status_code == 200
    kpi_data = kpi_res.json()
    assert kpi_data["total_wallets"] == "N/A"
    assert kpi_data["wallet_status"] == "NOT_PROVIDED"

def test_sih_synthetic_derived_wallets():
    """
    Verifies that SIH Synthetic mode derives address records dynamically
    from transaction inputs and outputs stored in SQLite.
    """
    # Force ingest synthetic data
    pipeline_service.generate_and_ingest_data(normal_count=20, include_anomalies=True)
    pipeline_service.execute_analytics_pipeline()

    res = client.get("/api/v1/wallets?dataset=synthetic")
    assert res.status_code == 200
    data = res.json()
    assert data["dataset_source"] == "sih_synthetic"
    assert data["status"] == "AVAILABLE"
    assert isinstance(data["wallets"], list)
    assert len(data["wallets"]) > 0

    # Verify derived address structure
    sample = data["wallets"][0]
    assert "address" in sample
    assert "num_txs_as_sender" in sample
    assert "num_txs_as_receiver" in sample
    assert "btc_transacted_total" in sample

    # Verify KPI summary
    kpi_res = client.get("/api/v1/overview/kpis?dataset=synthetic")
    assert kpi_res.status_code == 200
    kpi_data = kpi_res.json()
    assert isinstance(kpi_data["total_wallets"], int)
    assert kpi_data["total_wallets"] > 0
    assert kpi_data["wallet_status"] == "AVAILABLE"

def test_elliptic_v2_wallets():
    """
    Verifies that Elliptic++ v2 returns available wallet entities.
    """
    res = client.get("/api/v1/wallets?dataset=elliptic_v2")
    assert res.status_code == 200
    data = res.json()
    assert data["dataset_source"] == "elliptic_v2"
    assert data["status"] == "AVAILABLE"
    assert isinstance(data["wallets"], list)
