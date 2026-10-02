from typing import List, Dict, Any

class NetworkCleaner:
    """Standardizes, validates, and cleans network observation records."""
    
    @staticmethod
    def clean_observations(raw_observations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned = []
        for obs in raw_observations:
            txid = obs.get("txid", "").strip().lower()
            src_ip = obs.get("src_ip", "").strip()
            if not txid or not src_ip:
                continue
            
            cleaned_obs = {
                "obs_id": obs.get("obs_id", f"obs_{len(cleaned)}"),
                "timestamp": obs.get("timestamp"),
                "src_ip": src_ip,
                "dst_ip": obs.get("dst_ip", "").strip(),
                "src_port": int(obs.get("src_port", 8333)),
                "dst_port": int(obs.get("dst_port", 8333)),
                "txid": txid,
                "geo_country": obs.get("geo_country", "UNKNOWN").upper(),
                "asn": obs.get("asn", "UNKNOWN"),
                "time_delta": float(obs.get("time_delta", 0.0)),
                "network_event_type": obs.get("network_event_type", "tx_relay")
            }
            if "synthetic_scenario_label" in obs:
                cleaned_obs["synthetic_scenario_label"] = obs["synthetic_scenario_label"]
            cleaned.append(cleaned_obs)
        return cleaned
