import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple

class FeatureBuilder:
    """
    Feature Engineering Engine.
    Extracts address-level and transaction-level numerical feature matrices
    from preprocessed blockchain and network cross-layer observations.
    
    Excludes ground-truth evaluation labels (e.g. synthetic_scenario_label, is_change_ground_truth).
    """
    def __init__(
        self, 
        transactions: List[Dict[str, Any]], 
        network_observations: List[Dict[str, Any]]
    ):
        self.transactions = transactions
        self.network_observations = network_observations
        self.obs_by_txid: Dict[str, List[Dict[str, Any]]] = {}
        for obs in network_observations:
            txid = obs["txid"]
            if txid not in self.obs_by_txid:
                self.obs_by_txid[txid] = []
            self.obs_by_txid[txid].append(obs)

    def build_address_feature_matrix(self) -> pd.DataFrame:
        """
        Extracts address-level numerical features for Entity Clustering (DBSCAN) 
        and Anomaly Detection.
        """
        address_stats: Dict[str, Dict[str, Any]] = {}

        def get_addr_entry(addr: str) -> Dict[str, Any]:
            if addr not in address_stats:
                address_stats[addr] = {
                    "address": addr,
                    "tx_count": 0,
                    "sent_amount": 0,
                    "recv_amount": 0,
                    "inputs_as_common": 0,
                    "counterparties": set(),
                    "linked_ips": set(),
                    "linked_asns": set(),
                    "linked_countries": set(),
                    "time_deltas": []
                }
            return address_stats[addr]

        for tx in self.transactions:
            txid = tx["txid"]
            tx_inputs = tx.get("inputs", [])
            tx_outputs = tx.get("outputs", [])
            obs_list = self.obs_by_txid.get(txid, [])

            in_addrs = [inp["address"] for inp in tx_inputs if "address" in inp]
            out_addrs = [out["address"] for out in tx_outputs if "address" in out]

            # Common Input heuristic signal count
            is_multi_input = len(in_addrs) > 1

            for inp in tx_inputs:
                addr = inp.get("address")
                if not addr:
                    continue
                entry = get_addr_entry(addr)
                entry["tx_count"] += 1
                entry["sent_amount"] += inp.get("amount", 0)
                if is_multi_input:
                    entry["inputs_as_common"] += 1
                for out_addr in out_addrs:
                    entry["counterparties"].add(out_addr)

            for out in tx_outputs:
                addr = out.get("address")
                if not addr:
                    continue
                entry = get_addr_entry(addr)
                entry["tx_count"] += 1
                entry["recv_amount"] += out.get("amount", 0)
                for in_addr in in_addrs:
                    entry["counterparties"].add(in_addr)

            # Process linked network observations
            for obs in obs_list:
                ip = obs["src_ip"]
                asn = obs["asn"]
                country = obs["geo_country"]
                td = obs["time_delta"]

                for addr in set(in_addrs + out_addrs):
                    entry = get_addr_entry(addr)
                    entry["linked_ips"].add(ip)
                    entry["linked_asns"].add(asn)
                    entry["linked_countries"].add(country)
                    entry["time_deltas"].append(td)

        rows = []
        for addr, stats in address_stats.items():
            total_amount = stats["sent_amount"] + stats["recv_amount"]
            avg_td = float(np.mean(stats["time_deltas"])) if stats["time_deltas"] else 0.0
            
            rows.append({
                "address": addr,
                "tx_count": stats["tx_count"],
                "sent_amount": stats["sent_amount"],
                "recv_amount": stats["recv_amount"],
                "total_amount": total_amount,
                "common_input_signal": stats["inputs_as_common"],
                "unique_counterparties": len(stats["counterparties"]),
                "unique_ips": len(stats["linked_ips"]),
                "unique_asns": len(stats["linked_asns"]),
                "unique_countries": len(stats["linked_countries"]),
                "avg_time_delta": round(avg_td, 4)
            })

        df = pd.DataFrame(rows)
        if df.empty:
            return pd.DataFrame(columns=[
                "address", "tx_count", "sent_amount", "recv_amount", "total_amount",
                "common_input_signal", "unique_counterparties", "unique_ips",
                "unique_asns", "unique_countries", "avg_time_delta"
            ])
        return df

    def build_transaction_feature_matrix(self) -> pd.DataFrame:
        """
        Extracts transaction-level numerical features for Anomaly Detection (Isolation Forest),
        Peeling-Chain Detection, and Mixing Pattern Classification.
        """
        rows = []
        for tx in self.transactions:
            txid = tx["txid"]
            obs_list = self.obs_by_txid.get(txid, [])

            in_cnt = tx["input_count"]
            out_cnt = tx["output_count"]
            tot_amt = tx["total_input_amount"]
            fee = tx["fee"]
            fee_ratio = fee / max(1, tot_amt)
            entropy = tx.get("output_entropy", 0.0)

            td = float(np.mean([o["time_delta"] for o in obs_list])) if obs_list else 0.0
            unique_src_ips = len(set(o["src_ip"] for o in obs_list))

            rows.append({
                "txid": txid,
                "input_count": in_cnt,
                "output_count": out_cnt,
                "total_amount": tot_amt,
                "fee": fee,
                "fee_ratio": round(fee_ratio, 6),
                "output_entropy": entropy,
                "time_delta": round(td, 4),
                "unique_src_ips": unique_src_ips,
                "in_out_ratio": round(in_cnt / max(1, out_cnt), 4),
                "is_symmetric_in_out": 1 if (in_cnt > 1 and in_cnt == out_cnt) else 0
            })

        df = pd.DataFrame(rows)
        return df
