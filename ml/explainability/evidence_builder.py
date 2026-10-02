import json
from typing import Dict, Any, List

class EvidenceLineageBuilder:
    """
    Evidence & Data Lineage Generator.
    Builds human-understandable alert packages maintaining traceable lineage
    from risk scores back to underlying transactions, IPs, and feature contributions.
    """
    
    @staticmethod
    def build_evidence_pack(
        alert_id: str,
        target_type: str,
        target_id: str,
        alert_type: str,
        risk_score: float,
        confidence: float,
        risk_components: Dict[str, float],
        supporting_txids: List[str],
        supporting_ip_obs: List[str],
        narrative_reasons: List[str],
        time_range: str = "N/A"
    ) -> Dict[str, Any]:
        """
        Constructs traceable evidence JSON payload.
        """
        payload = {
            "alert_id": alert_id,
            "target_type": target_type,
            "target_id": target_id,
            "alert_type": alert_type,
            "risk_score": risk_score,
            "confidence": confidence,
            "evidence": {
                "detection_models": ["IsolationForest", "DBSCAN", "StructuralPatternAnalyzer"],
                "risk_components": risk_components,
                "contributing_features": narrative_reasons,
                "supporting_txids": supporting_txids[:10],
                "supporting_ip_obs": supporting_ip_obs[:10],
                "time_range": time_range,
                "summary": f"Alert {alert_id} generated for {target_type} {target_id} with Risk Score {risk_score}/100."
            }
        }
        return payload
