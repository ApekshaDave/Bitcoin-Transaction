import os
import json
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional

from backend.schemas import DataGenRequest, DatasetLoadRequest, PipelineRunRequest, KPISummary
from backend.services import PipelineService
from backend.database import DatabaseManager

app = FastAPI(
    title="SIH26146 Bitcoin Traffic Monitor API",
    description="Offline-Capable AI-Powered Bitcoin Transaction Traffic & Network Monitoring API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_manager = DatabaseManager()
pipeline_service = PipelineService(db_manager=db_manager)

@app.on_event("startup")
def startup_event():
    # Auto-generate baseline synthetic dataset and execute pipeline on startup
    pipeline_service.generate_and_ingest_data(normal_count=60, include_anomalies=True, seed=42)
    pipeline_service.execute_analytics_pipeline()

@app.get("/api/v1/health")
def health_check():
    return {"status": "online", "mode": "offline-capable"}

@app.post("/api/v1/dataset/load")
def load_dataset(req: DatasetLoadRequest):
    """
    Loads specified dataset ('synthetic', 'elliptic_v1', or 'elliptic_v2') and executes ML pipeline.
    """
    try:
        if req.dataset_type == "synthetic":
            res = pipeline_service.generate_and_ingest_data(normal_count=60, include_anomalies=True, seed=42)
            pipeline_service.execute_analytics_pipeline()
            return res
        else:
            res = pipeline_service.load_elliptic_dataset(
                dataset_type=req.dataset_type,
                time_step_limit=req.time_step_limit,
                max_txs=req.max_txs
            )
            return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/dataset/info")
def get_dataset_info(dataset: Optional[str] = Query(default=None)):
    """
    Returns metadata for active dataset including time steps, class counts, and metadata.
    """
    query = "SELECT * FROM dataset_metadata"
    params = []
    if dataset:
        query += " WHERE dataset_source = ?"
        params.append(dataset)
    query += " ORDER BY loaded_at DESC LIMIT 1"

    with db_manager.get_connection() as conn:
        row = conn.execute(query, params).fetchone()

    if row:
        return dict(row)

    return {
        "dataset_source": dataset or pipeline_service.active_dataset_source,
        "dataset_name": (dataset or pipeline_service.active_dataset_source).upper(),
        "status": "active"
    }

@app.post("/api/v1/generator/run")
def run_generator(req: DataGenRequest):
    try:
        res = pipeline_service.generate_and_ingest_data(
            normal_count=req.normal_count, 
            include_anomalies=req.include_anomalies, 
            seed=req.seed
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/pipeline/execute")
def execute_pipeline(req: PipelineRunRequest):
    try:
        res = pipeline_service.execute_analytics_pipeline(
            w_anomaly=req.w_anomaly, w_peeling=req.w_peeling,
            w_mixing=req.w_mixing, w_network=req.w_network, w_graph=req.w_graph
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/risk/recalculate")
def recalculate_risk_leads(req: PipelineRunRequest):
    """
    Recalculates multi-component risk scores and persists updated alerts into SQLite database.
    """
    try:
        res = pipeline_service.execute_analytics_pipeline(
            w_anomaly=req.w_anomaly, w_peeling=req.w_peeling,
            w_mixing=req.w_mixing, w_network=req.w_network, w_graph=req.w_graph
        )
        with db_manager.get_connection() as conn:
            alert_rows = conn.execute("SELECT * FROM alerts ORDER BY risk_score DESC LIMIT 50").fetchall()
        
        alerts = []
        for r in alert_rows:
            item = dict(r)
            item["evidence"] = json.loads(item.get("evidence_json", "{}")) if item.get("evidence_json") else {}
            alerts.append(item)

        return {
            "status": "success",
            "weights": {
                "w_anomaly": req.w_anomaly,
                "w_peeling": req.w_peeling,
                "w_mixing": req.w_mixing,
                "w_network": req.w_network,
                "w_graph": req.w_graph
            },
            "summary": res.get("summary", {}),
            "alerts": alerts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/overview/kpis")
def get_kpi_summary(dataset: Optional[str] = Query(default=None)):
    if dataset and dataset != pipeline_service.active_dataset_source:
        if dataset in ["elliptic_v1", "elliptic_v2"]:
            pipeline_service.load_elliptic_dataset(dataset_type=dataset)
        elif dataset in ["synthetic", "sih_synthetic"]:
            pipeline_service.generate_and_ingest_data()
            pipeline_service.execute_analytics_pipeline()
    elif not pipeline_service.latest_pipeline_results:
        pipeline_service.execute_analytics_pipeline()
    
    summary = pipeline_service.latest_pipeline_results.get("summary", {})
    return summary

@app.get("/api/v1/alerts")
def get_alerts(
    min_risk: float = Query(default=0.0, ge=0.0, le=100.0),
    dataset: Optional[str] = Query(default=None)
):
    with db_manager.get_connection() as conn:
        if dataset:
            rows = conn.execute(
                "SELECT * FROM alerts WHERE (dataset_source = ? OR dataset_source IS NULL) AND risk_score >= ? ORDER BY risk_score DESC",
                (dataset, min_risk)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM alerts WHERE risk_score >= ? ORDER BY risk_score DESC", 
                (min_risk,)
            ).fetchall()

    results = []
    for r in rows:
        item = dict(r)
        item["evidence"] = json.loads(item.get("evidence_json", "{}")) if item.get("evidence_json") else {}
        results.append(item)

    return results

@app.get("/api/v1/alerts/{alert_id}")
def get_alert_detail(alert_id: str):
    with db_manager.get_connection() as conn:
        row = conn.execute("SELECT * FROM alerts WHERE alert_id = ?", (alert_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")

    item = dict(row)
    item["evidence"] = json.loads(item.get("evidence_json", "{}")) if item.get("evidence_json") else {}
    return item

@app.get("/api/v1/transactions")
def get_transactions(
    class_label: Optional[int] = Query(default=None, description="1: Illicit, 2: Licit, 3: Unknown"),
    dataset: Optional[str] = Query(default=None),
    dataset_source: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """
    Returns transactions list with class filtering and pagination.
    """
    query = "SELECT * FROM transactions WHERE 1=1"
    params = []

    target_dataset = dataset or dataset_source
    if class_label is not None:
        query += " AND class_label = ?"
        params.append(class_label)
    if target_dataset is not None:
        ds_val = "synthetic" if target_dataset in ["synthetic", "sih_synthetic"] else target_dataset
        query += " AND dataset_source = ?"
        params.append(ds_val)

    query += " ORDER BY block_height DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with db_manager.get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    results = [dict(r) for r in rows]
    return results

@app.get("/api/v1/transactions/{txid}")
def get_transaction_detail(txid: str):
    with db_manager.get_connection() as conn:
        tx_row = conn.execute("SELECT * FROM transactions WHERE txid = ?", (txid,)).fetchone()
        if not tx_row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        tx = dict(tx_row)
        inp_rows = conn.execute("SELECT * FROM tx_inputs WHERE txid = ?", (txid,)).fetchall()
        out_rows = conn.execute("SELECT * FROM tx_outputs WHERE txid = ?", (txid,)).fetchall()
        obs_rows = conn.execute("SELECT * FROM network_observations WHERE txid = ?", (txid,)).fetchall()

        tx["inputs"] = [dict(i) for i in inp_rows]
        tx["outputs"] = [dict(o) for o in out_rows]
        tx["network_observations"] = [dict(ob) for ob in obs_rows]
        return tx

@app.get("/api/v1/wallets")
def get_wallets(
    dataset: Optional[str] = Query(default=None),
    dataset_source: Optional[str] = Query(default=None),
    class_label: Optional[int] = Query(default=None, description="1: Illicit, 2: Licit, 3: Unknown"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """
    Returns dataset-scoped wallet entities.
    - Elliptic v1: Returns NOT_PROVIDED status ("N/A — wallet dataset not provided").
    - Elliptic v2: Returns loaded Elliptic++ wallet entities.
    - SIH Synthetic: Returns derived address records from transaction inputs/outputs.
    """
    target_ds = dataset or dataset_source or pipeline_service.active_dataset_source

    if target_ds == "elliptic_v1":
        return {
            "dataset_source": "elliptic_v1",
            "status": "NOT_PROVIDED",
            "message": "N/A — wallet dataset not provided by Elliptic v1 benchmark",
            "total_count": "N/A",
            "wallets": []
        }

    if target_ds in ["synthetic", "sih_synthetic"]:
        derived = pipeline_service.get_synthetic_derived_wallets(limit=limit, offset=offset)
        return {
            "dataset_source": "sih_synthetic",
            "status": "AVAILABLE",
            "total_count": len(derived),
            "wallets": derived
        }

    query = "SELECT * FROM wallets WHERE 1=1"
    params = []
    if class_label is not None:
        query += " AND class_label = ?"
        params.append(class_label)

    query += " ORDER BY btc_transacted_total DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with db_manager.get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        w_list = [dict(r) for r in rows]

    return {
        "dataset_source": "elliptic_v2",
        "status": "AVAILABLE",
        "total_count": len(w_list),
        "wallets": w_list
    }

@app.get("/api/v1/network/observations")
def get_network_observations(
    dataset: Optional[str] = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """
    Returns dataset-scoped network observations with explicit provenance metadata.
    """
    target_dataset = dataset or pipeline_service.active_dataset_source
    ds_val = "synthetic" if target_dataset in ["synthetic", "sih_synthetic"] else target_dataset

    with db_manager.get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM network_observations WHERE dataset_source = ? LIMIT ? OFFSET ?",
            (ds_val, limit, offset)
        ).fetchall()

    obs_list = [dict(r) for r in rows]

    # Fallback to general query if specific dataset query returned empty
    if not obs_list:
        with db_manager.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM network_observations LIMIT ? OFFSET ?",
                (limit, offset)
            ).fetchall()
        obs_list = [dict(r) for r in rows]

    # Ensure provenance fields exist on every item
    for o in obs_list:
        o["network_data_source"] = "synthetic"
        o["network_data_provenance"] = "project_generated"
        o["network_data_scope"] = "synthetic_network_simulation" if target_dataset in ["elliptic_v1", "elliptic_v2"] else "sih_synthetic_network"
        o["geo_source"] = "synthetic"
        o["asn_source"] = "synthetic"

    return {
        "dataset_source": target_dataset,
        "network_data_source": "synthetic",
        "network_data_provenance": "project_generated",
        "network_data_scope": "synthetic_network_simulation" if target_dataset in ["elliptic_v1", "elliptic_v2"] else "sih_synthetic_network",
        "geo_source": "synthetic",
        "asn_source": "synthetic",
        "total_count": len(obs_list),
        "observations": obs_list
    }

@app.get("/api/v1/ml/status")
def get_ml_status(dataset: Optional[str] = Query(default=None)):
    """
    Returns active ML status, model artifact paths, training metadata, metrics, and diagnostic report.
    """
    target_ds = dataset or pipeline_service.active_dataset_source
    if target_ds in ["synthetic", "sih_synthetic"]:
        target_ds = "elliptic_v2" # benchmark metrics source for models

    models_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", target_ds))

    schema_file = os.path.join(models_base, "feature_schema.json")
    meta_file = os.path.join(models_base, "training_metadata.json")
    eval_file = os.path.join(models_base, "evaluation_report.json")
    diag_file = os.path.join(models_base, "ml_diagnostic_report.json")
    comp_file = os.path.join(models_base, "final_ml_comparison.json")

    schema_data = json.load(open(schema_file)) if os.path.exists(schema_file) else {}
    meta_data = json.load(open(meta_file)) if os.path.exists(meta_file) else {}
    eval_data = json.load(open(eval_file)) if os.path.exists(eval_file) else {}
    diag_data = json.load(open(diag_file)) if os.path.exists(diag_file) else {}
    comp_data = json.load(open(comp_file)) if os.path.exists(comp_file) else {}

    return {
        "active_dataset_source": pipeline_service.active_dataset_source,
        "requested_dataset": dataset or pipeline_service.active_dataset_source,
        "models_dir": models_base,
        "artifacts_exist": {
            "isolation_forest": os.path.exists(os.path.join(models_base, "isolation_forest.pkl")),
            "logistic_regression": os.path.exists(os.path.join(models_base, "logistic_regression.pkl")),
            "random_forest": os.path.exists(os.path.join(models_base, "random_forest.pkl")),
            "scaler": os.path.exists(os.path.join(models_base, "scaler.pkl")),
            "dbscan": os.path.exists(os.path.join(models_base, "dbscan.pkl")),
            "diagnostic_report": os.path.exists(diag_file),
            "final_comparison": os.path.exists(comp_file)
        },
        "feature_schema": schema_data,
        "training_metadata": meta_data,
        "evaluation_metrics": eval_data,
        "diagnostic_report": diag_data,
        "final_comparison": comp_data
    }

@app.get("/api/v1/investigation/trace/{tx_id}")
def get_investigation_trace(tx_id: str):
    """
    Returns end-to-end investigation trace across network, transaction, address,
    entity, ML, graph, and risk layers.
    """
    return pipeline_service.get_investigation_trace(tx_id)

@app.get("/api/v1/graph")
def get_graph(
    dataset: Optional[str] = Query(default=None),
    tx_id: Optional[str] = Query(default=None),
    center: Optional[str] = Query(default=None),
    depth: int = Query(default=1, ge=1, le=3),
    limit: int = Query(default=50, ge=5, le=200)
):
    """
    Returns bounded Cytoscape.js heterogeneous graph elements payload (nodes, edges) 
    for active or specified dataset scope, centered on target node up to depth and max limit.
    """
    target_dataset = dataset or pipeline_service.active_dataset_source
    if dataset and dataset != pipeline_service.active_dataset_source:
        if dataset in ["elliptic_v1", "elliptic_v2"]:
            pipeline_service.load_elliptic_dataset(dataset_type=dataset)
        elif dataset in ["synthetic", "sih_synthetic"]:
            pipeline_service.generate_and_ingest_data()
            pipeline_service.execute_analytics_pipeline()
    elif not pipeline_service.latest_pipeline_results:
        pipeline_service.execute_analytics_pipeline()

    # Re-extract bounded subgraph using graph builder
    center_target = center or tx_id or "tx_golden_001"
    
    # Check if pipeline_service has built NetworkX graph
    txs, obs, wallets, _ = pipeline_service.db.load_latest_data()
    from graph.graph_builder import HeterogeneousGraphBuilder
    gb = HeterogeneousGraphBuilder()
    gb.build_graph(txs, obs)
    
    subgraph_payload = gb.export_to_cytoscape_json(
        center_node_id=center_target,
        depth=depth,
        max_nodes=limit,
        max_edges=limit * 2
    )
    subgraph_payload["dataset"] = target_dataset
    return subgraph_payload

@app.get("/api/v1/graph/subgraph")
def get_graph_subgraph(
    center_node_id: Optional[str] = Query(default=None),
    dataset: Optional[str] = Query(default=None),
    depth: int = Query(default=2, ge=1, le=4)
):
    if not pipeline_service.latest_pipeline_results:
        pipeline_service.execute_analytics_pipeline()
    
    graph_data = pipeline_service.latest_pipeline_results.get("graph", {"elements": []})
    
    # If center_node_id provided, ensure it returns relevant nodes/edges
    if center_node_id and graph_data and "elements" in graph_data:
        filtered_elements = []
        node_ids = set([center_node_id])
        
        # Collect edges connected to center_node_id
        for el in graph_data["elements"]:
            data = el.get("data", {})
            if "source" in data and "target" in data:
                if data["source"] == center_node_id or data["target"] == center_node_id:
                    filtered_elements.append(el)
                    node_ids.add(data["source"])
                    node_ids.add(data["target"])

        # Collect node elements matching node_ids
        for el in graph_data["elements"]:
            data = el.get("data", {})
            if "id" in data and data["id"] in node_ids:
                if el not in filtered_elements:
                    filtered_elements.append(el)

        if filtered_elements:
            return {"elements": filtered_elements}

    return graph_data

@app.get("/api/v1/analytics/models")
def get_model_evaluation_report():
    if not pipeline_service.latest_pipeline_results:
        pipeline_service.execute_analytics_pipeline()

    eval_metrics = pipeline_service.latest_pipeline_results.get("evaluation_metrics", {})
    return eval_metrics

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
