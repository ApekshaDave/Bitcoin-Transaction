# SIH26146 — Dataset & Provenance Documentation

## 1. Overview & Dataset Dual Scope

The **SIH26146 Bitcoin Traffic Monitoring Platform** operates under two distinct, explicit data modes:

1. **Elliptic / Elliptic++ Public ML Benchmark Mode**:
   - Used strictly for academic/research ML model training, feature importance analysis, and benchmark evaluation on public transaction and wallet/actor graphs.
   - Elliptic v1: 165 numerical features (+ txId, time_step = 167 columns).
   - Elliptic++ v2: 182 numerical features (+ txId, Time step = 184 columns).
   - **Network Telemetry Policy**: Public blockchain datasets contain **0 fake/fabricated P2P network telemetry** (`src_ip`, `dst_ip`, `geo_country`). When Elliptic datasets are active, the network layer reports `"Public Blockchain Data (No P2P network telemetry)"`.

2. **SIH Synthetic Cross-Layer Investigation Mode**:
   - Used for end-to-end SOC investigative workflow demonstrations, multi-layer correlation, and 9-stage provenance tracing.
   - Generates 100% correlated Bitcoin transactions, multi-address inputs/outputs, entity clusters, and P2P relay observations (`src_ip`, `dst_ip`, `src_port`, `dst_port`, `geo_country`, `asn`, `time_delta`, `network_event_type`).

---

## 2. Elliptic++ Dataset Structure

### Transaction Layer Files
- `txs_features.csv`: 203,769 transactions across 49 time steps. 182 numerical features per transaction.
- `txs_classes.csv`: Ground-truth labels: `1` (Illicit), `2` (Licit), `3` (Unknown). Note: Class 3 is excluded from supervised training and binary metrics.
- `txs_edgelist.csv`: Directed graph payment edges between transaction IDs (`txId1` -> `txId2`).

### Actor / Wallet Layer Files
- `wallets_features.csv`: 1,268,260 temporal address/wallet observation records across 49 time steps (representing unique address-step snapshots).
- `wallets_classes.csv`: Ground-truth actor labels.
- `AddrAddr_edgelist.csv`: Address-to-Address directed transaction flow edges.
- `AddrTx_edgelist.csv`: Address-to-Transaction input spending edges.
- `TxAddr_edgelist.csv`: Transaction-to-Address output payment edges.

---

## 3. Synthetic Cross-Layer Data Generator (`data_generator/`)

The synthetic data engine produces deterministic, realistic traffic scenarios:
- **Normal Financial Activity**: Standard wallet transfers, P2PKH/P2WPKH outputs, multi-input consolidation.
- **Peeling Chain Anomaly**: Sequential change outputs carrying decreasing amounts to obfuscate main fund flows. Includes golden case `TX_GOLDEN_001` (`CASE-001`).
- **Mixing Pool Obfuscation**: Equal-value output transactions mimicking CoinJoin mixing pools.
- **Network Traffic Burst**: P2P relay spikes with sub-100ms propagation delays and multi-node relay logs.

---

## 4. Ground-Truth & Feature Matrix Isolation

To strictly prevent data leakage and benchmark gaming:
- `class_label` is **never included** in any feature matrix $X$ provided to Isolation Forest, DBSCAN, Logistic Regression, or Random Forest.
- `class_label` is loaded separately into target vector $y$ and used solely during evaluation metric computation (ROC-AUC, PR-AUC, F1).
- Unsupervised Isolation Forest and DBSCAN execute on unlabeled feature spaces.
