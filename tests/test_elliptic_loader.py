import pytest
import os
from preprocessing.elliptic_loader import (
    EllipticDatasetLoader, EllipticV1Loader, EllipticV2Loader, SyntheticLoader
)

def test_elliptic_v1_loader_data_integrity():
    loader = EllipticDatasetLoader.get_loader("elliptic_v1", time_step_limit=2, max_txs=50)
    data = loader.load_data()

    assert data["dataset_source"] == "elliptic_v1"
    assert len(data["transactions"]) > 0
    assert len(data["network_observations"]) == 0  # Zero fabricated network data for public dataset!
    
    tx = data["transactions"][0]
    assert "txid" in tx
    assert "class_label" in tx
    assert tx["dataset_source"] == "elliptic_v1"
    assert tx["class_label"] in [1, 2, 3]

def test_elliptic_v2_loader_data_integrity():
    loader = EllipticDatasetLoader.get_loader("elliptic_v2", time_step_limit=2, max_txs=50)
    data = loader.load_data()

    assert data["dataset_source"] == "elliptic_v2"
    assert len(data["transactions"]) > 0
    assert len(data["wallets"]) > 0
    assert "edges" in data

    wallet = data["wallets"][0]
    assert "address" in wallet
    assert "class_label" in wallet
    assert "num_txs_as_sender" in wallet

def test_synthetic_loader_cross_layer_integrity():
    loader = EllipticDatasetLoader.get_loader("synthetic")
    data = loader.load_data()

    assert data["dataset_source"] == "synthetic"
    assert len(data["transactions"]) > 0
    assert len(data["network_observations"]) > 0  # Contains cross-layer IP/port network data!
