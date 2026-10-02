# AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic

**Smart India Hackathon 2026 Problem Statement**: SIH26146  
**Organization**: National Technical Research Organisation (NTRO)  
**Category**: Software | **Theme**: Blockchain & Cybersecurity  

---

## 📌 Executive Summary

This platform is an **offline-capable, AI-driven Bitcoin transaction and P2P network monitoring platform** designed for technical intelligence analysts. It fuses on-chain blockchain transaction lineage with P2P network traffic observations to detect illegal financial activity, high-risk peeling chains, mixing obfuscation networks, and correlated IP clusters.

The system supports strict **dataset isolation** across three operational modes:
1. **SIH Synthetic Investigation**: Multi-layer investigative mode featuring synthetic IP relay observations, wallet clusters, address mappings, and deterministic investigation targets (e.g., `TX_GOLDEN_001` / `CASE-001`).
2. **Elliptic v1 Benchmark**: 204,917 transactions across 49 time steps for standard baseline evaluations.
3. **Elliptic++ ML Benchmark**: 203,769 transactions with actor-level background features, evaluated across strict temporal train/validation/test splits.

---

## 🚀 Key Architectural Features

### 1. Synthetic Data Generator (`data_generator/`)
- Generates realistic Bitcoin transaction DAGs with `prev_txid` and `prev_vout_index` input spending pointers.
- Generates correlated P2P relay observations (`src_ip`, `dst_ip`, `geo_country`, `asn`, `time_delta`).
- Generates controlled scenario benchmarks: Normal traffic, Peeling Chains, Mixing Obfuscation, and Network Traffic Bursts.

### 2. Preprocessing & Dataset Loaders (`preprocessing/`)
- Integrates IP observations with blockchain addresses and transactions.
- Provides dedicated dataset loaders for `sih_synthetic`, `elliptic_v1`, and `elliptic_v2` datasets.
- Extracts address-level and transaction-level numerical feature matrices (`feature_builder.py`).

### 3. Server-Side Bounded Graph Engine (`graph/`, `backend/`)
- Builds NetworkX heterogeneous multi-graphs featuring node types: `IP`, `Transaction`, `Address`, `Entity`.
- **Canonical Edge Relationships**:
  - `(IP) -[OBSERVED]-> (Transaction)`
  - `(Address) -[INPUT]-> (Transaction)`
  - `(Transaction) -[OUTPUT]-> (Address)`
  - `(Address) -[ASSOCIATED_WITH]-> (Entity)`
- **Bounded Subgraph Queries**: Implements server-side neighborhood extraction (`GET /api/v1/graph?tx_id=...&depth=...&limit=...`) with hard safety limits (`MAX_GRAPH_NODES = 200`, `MAX_GRAPH_EDGES = 500`) to guarantee high frontend performance and zero browser freezes.

### 4. Multi-Stage AI/ML Pipeline & Benchmarks (`ml/`)
- **Entity Clustering**: DBSCAN address clustering (`entity_clusterer.py`).
- **Unsupervised Anomaly Detection**: Isolation Forest outlier scoring (`anomaly_detector.py`).
- **Supervised ML Benchmark**: Evaluated on Elliptic++ using chronological splits (Train: Steps 1–30, Validation: Steps 31–40, Test: Steps 41–49):
  - **Isolation Forest**: ROC-AUC = 0.2439, PR-AUC = 0.0316
  - **Logistic Regression**: ROC-AUC = 0.781, PR-AUC = 0.542
  - **Random Forest**: ROC-AUC = 0.812, PR-AUC = 0.621
- **Structural Pattern Classifiers**: Peeling chain detection (`peeling_detector.py`) and mixing pool detection (`mixing_detector.py`).
- **Configurable Risk Engine**: Computes normalized $0 - 100$ score via $100 \times \sum w_i S_i$.
- **9-Stage Provenance Lineage**: Produces end-to-end investigation trace payloads via `/api/v1/investigation/trace/{tx_id}`.

### 5. Interactive SOC Investigation Dashboard (`frontend/`)
- React + Vite + Cytoscape.js + Tailwind CSS.
- Features: Real-time System Status Navbar, KPI Metric Cards, Scoped Alert Queue, Evidence Lineage Side-Drawer, Bounded Cytoscape Graph Explorer with **Graph Scope** widget, and Transaction Inspector.

---

## 🛠️ System Requirements & Setup

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/ApekshaDave/Bitcoin-Transaction.git
cd Bitcoin-Transaction

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install backend dependencies
pip install -r requirements.txt

# 4. Install frontend dependencies
cd frontend
npm install
cd ..

# 5. Execute test suite (29 tests)
python -m pytest tests/ -v

# 6. Launch Backend API
python -m uvicorn backend.main:app --reload --port 8000
```

### Frontend Development & Build

```bash
cd frontend
npm run dev     # Development server (http://localhost:5173)
npm run build   # Production bundle validation
```

---

## 🐳 Offline Docker Container Deployment

To launch the system in an offline, air-gapped Linux deployment:

```bash
docker-compose up --build -d
```

Or execute the launch script:

```bash
chmod +x start_offline_system.sh
./start_offline_system.sh
```

Access the dashboard at **`http://localhost:8000`**.

---

## 🧪 Testing & Verification

Run the full pytest suite to validate dataset loaders, ML pipelines, graph construction, risk scoring, alerts, and Golden Case integration:

```bash
python -m pytest tests/ -v
```

Output: **`29 passed in ~58s`**

---

## 📄 License & Team Credits

Built for **Smart India Hackathon 2026 (SIH26146)** by Team Apeksha Dave. Developed for National Technical Research Organisation (NTRO) offline deployment requirements.
