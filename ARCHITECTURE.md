# SIH26146 — System Architecture Documentation

## 1. System Architecture & Component Diagram

The **SIH26146 Bitcoin Traffic Monitoring Platform** provides cross-layer visibility by correlating P2P network telemetry with on-chain Bitcoin transactions.

```
       +-----------------------------------------------------------+
       |                  REACT / VITE FRONTEND                    |
       |  System Navbar | Alerts Queue | Cytoscape Graph | Trace   |
       +-----------------------------+-----------------------------+
                                     | REST API calls (JSON)
       +-----------------------------v-----------------------------+
       |                     FASTAPI BACKEND                       |
       |      Main Router (backend/main.py)                        |
       |      Pipeline Service (backend/services.py)               |
       |      SQLite Storage (backend/database.py)                 |
       +-----------------------------+-----------------------------+
                                     | Invokes Analytics Engine
       +-----------------------------v-----------------------------+
       |               CROSS-LAYER ANALYTICS ENGINE                |
       | 1. Cross-Layer Correlator (preprocessing/)                |
       | 2. Heterogeneous Graph Builder (graph/)                  |
       | 3. Multi-Input Address Clusterer (ml/clustering/)         |
       | 4. Isolation Forest & Supervised ML (ml/)                 |
       | 5. Structural Pattern Classifiers (ml/peeling, mixing)     |
       | 6. Prioritized Risk Engine (ml/risk_scoring/)            |
       +-----------------------------------------------------------+
```

---

## 2. 9-Stage Investigation Trace Service

The primary investigative endpoint `GET /api/v1/investigation/trace/{tx_id}` returns a 9-stage provenance trace:

1. **Network Observation**: IP endpoints, ports, country, ASN, propagation delay.
2. **TXID Correlation**: Matching between P2P relay events and transactions.
3. **Blockchain Transaction**: Fees, block height, inputs, outputs, timestamps.
4. **Input / Output Addresses**: Input prev_txid spending pointers and output script types.
5. **Entity Association**: Multi-input heuristic entity clustering (`inferred_entity_id`).
6. **Graph Context**: Cytoscape subgraph nodes and typed edges.
7. **ML Signals**: Isolation Forest anomaly scores & Random Forest illicit probabilities.
8. **Composite Risk Score**: Weighted risk formula $R = 100 \times [0.25 S_{\text{anomaly}} + 0.25 S_{\text{peeling}} + 0.20 S_{\text{mixing}} + 0.15 S_{\text{network}} + 0.15 S_{\text{graph}}]$.
9. **Explainable Alert**: Human-readable alert summary and recommended analyst actions.

---

## 3. Database Schema (`backend/database.py`)

The SQLite storage schema comprises 6 core tables:
- `transactions`: Core transaction properties (`txid`, `timestamp`, `fee`, `size`, `weight`, `block_height`, `input_count`, `output_count`, `total_input_amount`, `total_output_amount`, `synthetic_scenario_label`, `dataset_source`).
- `tx_inputs`: Input spending records (`txid`, `vin_index`, `prev_txid`, `prev_vout_index`, `address`, `amount`).
- `tx_outputs`: Output payment records (`txid`, `vout_index`, `address`, `amount`, `script_type`, `is_change_ground_truth`).
- `network_observations`: Correlated P2P telemetry (`obs_id`, `src_ip`, `dst_ip`, `src_port`, `dst_port`, `geo_country`, `asn`, `time_delta`, `network_event_type`, `txid`, `timestamp`).
- `entity_clusters`: Inferred behavioral entity groupings (`entity_id`, `clustering_method`, `cluster_quality_note`, `address_count`, `created_at`).
- `alerts`: Prioritized security alerts (`alert_id`, `target_type`, `target_id`, `risk_score`, `confidence`, `alert_type`, `created_at`, `evidence_json`).

---

## 4. Prioritization Risk Engine & Legal Disclaimer

Risk scores are computed using the project-defined weighted formula:
$$R = 100 \times (0.25 S_{\text{anomaly}} + 0.25 S_{\text{peeling}} + 0.20 S_{\text{mixing}} + 0.15 S_{\text{network}} + 0.15 S_{\text{graph}})$$

> [!IMPORTANT]
> **Legal & Regulatory Disclaimer**: Risk score is a project-defined prioritization score. It is not a probability of criminal activity and does not establish wrongdoing.
