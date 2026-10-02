from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class DataGenRequest(BaseModel):
    normal_count: int = Field(default=50, ge=10, le=500)
    include_anomalies: bool = Field(default=True)
    seed: int = Field(default=42)

class DatasetLoadRequest(BaseModel):
    dataset_type: str = Field(default="elliptic_v2", description="synthetic, elliptic_v1, or elliptic_v2")
    time_step_limit: Optional[int] = Field(default=5, ge=1, le=49)
    max_txs: Optional[int] = Field(default=1000, ge=10, le=50000)

class PipelineRunRequest(BaseModel):
    w_anomaly: float = 0.25
    w_peeling: float = 0.25
    w_mixing: float = 0.20
    w_network: float = 0.15
    w_graph: float = 0.15

class AlertResponse(BaseModel):
    alert_id: str
    target_type: str
    target_id: str
    risk_score: float
    confidence: float
    alert_type: str
    created_at: str
    evidence: Dict[str, Any]

class KPISummary(BaseModel):
    total_transactions: int
    total_network_observations: int
    total_entities: int
    total_alerts: int
    high_risk_alerts_count: int
    avg_risk_score: float
    scenario_distribution: Dict[str, int]
