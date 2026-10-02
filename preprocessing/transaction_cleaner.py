import math
from typing import List, Dict, Any

class TransactionCleaner:
    """Standardizes, validates, and cleans raw Bitcoin transaction records."""
    
    @staticmethod
    def clean_transactions(raw_transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cleaned = []
        for tx in raw_transactions:
            txid = tx.get("txid", "").strip().lower()
            if not txid or len(txid) < 10:
                continue
            
            inputs = tx.get("inputs", [])
            outputs = tx.get("outputs", [])
            
            total_in = sum(inp.get("amount", 0) for inp in inputs)
            total_out = sum(out.get("amount", 0) for out in outputs)
            fee = tx.get("fee", max(0, total_in - total_out))
            
            # Compute output entropy (for mixing detection)
            amounts = [out.get("amount", 0) for out in outputs if out.get("amount", 0) > 0]
            entropy = 0.0
            if total_out > 0 and len(amounts) > 1:
                probs = [amt / total_out for amt in amounts]
                entropy = -sum(p * math.log2(p) for p in probs if p > 0)

            cleaned_tx = {
                "txid": txid,
                "timestamp": tx.get("timestamp"),
                "fee": fee,
                "size": tx.get("size", 250),
                "weight": tx.get("weight", 1000),
                "block_height": tx.get("block_height", 800000),
                "input_count": len(inputs),
                "output_count": len(outputs),
                "total_input_amount": total_in,
                "total_output_amount": total_out,
                "output_entropy": round(entropy, 4),
                "inputs": inputs,
                "outputs": outputs
            }
            if "synthetic_scenario_label" in tx:
                cleaned_tx["synthetic_scenario_label"] = tx["synthetic_scenario_label"]
            cleaned.append(cleaned_tx)
        return cleaned

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
