from typing import Dict, Any, List, Optional

class RiskEngine:
    """
    Configurable Risk & Confidence Scoring Engine.
    
    Formula:
    Risk Score = 100 * sum(w_i * S_i) where sum(w_i) = 1.0 and S_i in [0, 1].
    
    Confidence Score:
    Independent metric [0.0, 1.0] representing evidence stability and multi-model agreement.
    """
    def __init__(
        self,
        w_anomaly: float = 0.25,
        w_peeling: float = 0.25,
        w_mixing: float = 0.20,
        w_network: float = 0.15,
        w_graph: float = 0.15
    ):
        self.weights = {
            "anomaly": w_anomaly,
            "peeling": w_peeling,
            "mixing": w_mixing,
            "network": w_network,
            "graph": w_graph
        }
        # Normalize weights if sum != 1.0
        tot_w = sum(self.weights.values())
        if tot_w > 0:
            for k in self.weights:
                self.weights[k] /= tot_w

    def calculate_risk_and_confidence(
        self,
        anomaly_score: float,
        peeling_score: float,
        mixing_score: float,
        network_burst_score: float,
        graph_score: float,
        observation_count: int = 1,
        model_agreements: int = 1
    ) -> Dict[str, Any]:
        """
        Calculates normalized Risk Score [0 - 100] and separate Confidence Score [0.0 - 1.0].
        """
        s_anomaly = max(0.0, min(1.0, float(anomaly_score)))
        s_peeling = max(0.0, min(1.0, float(peeling_score)))
        s_mixing = max(0.0, min(1.0, float(mixing_score)))
        s_network = max(0.0, min(1.0, float(network_burst_score)))
        s_graph = max(0.0, min(1.0, float(graph_score)))

        weighted_sum = (
            self.weights["anomaly"] * s_anomaly +
            self.weights["peeling"] * s_peeling +
            self.weights["mixing"] * s_mixing +
            self.weights["network"] * s_network +
            self.weights["graph"] * s_graph
        )

        risk_score = round(100.0 * weighted_sum, 2)

        # Confidence calculation based on evidence volume and agreement
        obs_confidence = min(1.0, 0.4 + 0.1 * min(observation_count, 6))
        agreement_factor = min(1.0, 0.5 + 0.25 * model_agreements)
        confidence = round(0.5 * obs_confidence + 0.5 * agreement_factor, 2)

        return {
            "risk_score": risk_score,
            "confidence": confidence,
            "components": {
                "anomaly": round(s_anomaly, 4),
                "peeling": round(s_peeling, 4),
                "mixing": round(s_mixing, 4),
                "network_burst": round(s_network, 4),
                "graph_centrality": round(s_graph, 4)
            },
            "weights": self.weights
        }
