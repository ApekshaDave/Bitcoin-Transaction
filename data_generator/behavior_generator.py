import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from data_generator.bitcoin_generator import BitcoinDataGenerator
from data_generator.network_generator import NetworkDataGenerator
from data_generator.geoip_generator import GeoIPASNEnricher

class SyntheticScenarioGenerator:
    """
    Orchestrates synthetic dataset generation with controlled behavioral scenarios:
    - Scenario 1: Normal Bitcoin activity
    - Scenario 2: High-Frequency / Bot activity
    - Scenario 3: Peeling-Chain activity
    - Scenario 4: Mixing-Like pattern structure
    - Scenario 5: IP Burst anomaly
    - Combined Benchmark dataset with synthetic_scenario_label (evaluation ground truth).
    """
    def __init__(self, seed: int = 42):
        self.enricher = GeoIPASNEnricher()
        self.btc_gen = BitcoinDataGenerator(seed=seed)
        self.net_gen = NetworkDataGenerator(enricher=self.enricher, seed=seed)
        self.btc_gen.create_genesis_utxos(count=100)

    def _get_timestamp_str(self, base_time: datetime, offset_seconds: float) -> str:
        dt = base_time + timedelta(seconds=offset_seconds)
        return dt.isoformat() + "Z"

    def generate_peeling_chain_scenario(
        self, 
        chain_length: int = 6, 
        base_time: datetime = None
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Generates a Peeling-Chain scenario:
        1 input -> 1 large continuation output + 1 small payment output, repeated across steps.
        Associated with a primary IP address across consecutive time intervals.
        """
        base_time = base_time or datetime.utcnow()
        tx_list = []
        obs_list = []
        
        peeling_ip = random.choice(self.net_gen.ip_pool)
        
        # Start with an initial UTXO
        if not self.btc_gen.unspent_outputs:
            self.btc_gen.create_genesis_utxos(10)
        current_utxo = self.btc_gen.unspent_outputs.pop(0)

        for step in range(chain_length):
            ts_str = self._get_timestamp_str(base_time, step * 45)  # 45-second intervals
            continuation_addr = self.btc_gen.address_pool[(step + 1) % len(self.btc_gen.address_pool)]
            payment_addr = self.btc_gen.address_pool[(step + 5) % len(self.btc_gen.address_pool)]
            
            total_amt = current_utxo["amount"]
            pay_amt = int(total_amt * 0.05)  # 5% payment
            cont_amt = total_amt - pay_amt - 2000  # 95% continuation - fee

            forced_outputs = [
                (continuation_addr, cont_amt, True),   # Change / Continuation output
                (payment_addr, pay_amt, False)         # Small payment output
            ]

            tx = self.btc_gen.generate_single_transaction(
                timestamp=ts_str,
                forced_inputs=[current_utxo],
                forced_outputs=forced_outputs
            )
            tx["synthetic_scenario_label"] = "peeling_chain"
            tx_list.append(tx)

            obs = self.net_gen.generate_observation_for_tx(
                txid=tx["txid"],
                tx_timestamp=ts_str,
                override_src_ip=peeling_ip,
                event_type="tx_relay"
            )
            obs["synthetic_scenario_label"] = "peeling_chain"
            obs_list.append(obs)

            # Set current_utxo for next peeling link (using continuation output vout 0)
            current_utxo = {
                "txid": tx["txid"],
                "vout_index": 0,
                "address": continuation_addr,
                "amount": cont_amt
            }

        return tx_list, obs_list

    def generate_mixing_scenario(
        self, 
        mix_count: int = 3, 
        base_time: datetime = None
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Generates a Mixing-Like scenario (Equalized multi-input multi-output transactions).
        """
        base_time = base_time or datetime.utcnow()
        tx_list = []
        obs_list = []

        for mix_idx in range(mix_count):
            ts_str = self._get_timestamp_str(base_time, mix_idx * 120)
            
            # Select 4 inputs of identical amounts
            equal_amt = 10000000  # 0.1 BTC
            inputs = []
            for i in range(4):
                addr = self.btc_gen.address_pool[i % len(self.btc_gen.address_pool)]
                inputs.append({
                    "txid": f"mix_input_seed_{mix_idx}_{i}",
                    "vout_index": i,
                    "address": addr,
                    "amount": equal_amt
                })

            # 4 outputs of equal amounts (minus fees)
            out_amt = equal_amt - 2500
            outputs = [
                (self.btc_gen.address_pool[(10 + j) % len(self.btc_gen.address_pool)], out_amt, False)
                for j in range(4)
            ]

            tx = self.btc_gen.generate_single_transaction(
                timestamp=ts_str,
                forced_inputs=inputs,
                forced_outputs=outputs
            )
            tx["synthetic_scenario_label"] = "mixing_pattern"
            tx_list.append(tx)

            obs = self.net_gen.generate_observation_for_tx(
                txid=tx["txid"],
                tx_timestamp=ts_str,
                event_type="coinjoin_relay"
            )
            obs["synthetic_scenario_label"] = "mixing_pattern"
            obs_list.append(obs)

        return tx_list, obs_list

    def generate_ip_burst_anomaly(
        self, 
        burst_size: int = 15, 
        base_time: datetime = None
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Generates an IP Burst Anomaly:
        A single source IP broadcasting dozens of distinct transactions within seconds.
        """
        base_time = base_time or datetime.utcnow()
        tx_list = []
        obs_list = []

        burst_ip = random.choice(self.net_gen.ip_pool)

        for i in range(burst_size):
            ts_str = self._get_timestamp_str(base_time, i * 0.1)  # 100ms rapid burst
            tx = self.btc_gen.generate_single_transaction(timestamp=ts_str)
            tx["synthetic_scenario_label"] = "ip_burst_anomaly"
            tx_list.append(tx)

            obs = self.net_gen.generate_observation_for_tx(
                txid=tx["txid"],
                tx_timestamp=ts_str,
                override_src_ip=burst_ip,
                event_type="rapid_burst"
            )
            obs["synthetic_scenario_label"] = "ip_burst_anomaly"
            obs_list.append(obs)

        return tx_list, obs_list

    def generate_normal_traffic(
        self, 
        count: int = 50, 
        base_time: datetime = None
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Generates standard, unflagged Bitcoin transactions and P2P observations.
        """
        base_time = base_time or datetime.utcnow()
        tx_list = []
        obs_list = []

        for i in range(count):
            ts_str = self._get_timestamp_str(base_time, i * 30)
            tx = self.btc_gen.generate_single_transaction(timestamp=ts_str)
            tx["synthetic_scenario_label"] = "normal"
            tx_list.append(tx)

            obs = self.net_gen.generate_observation_for_tx(
                txid=tx["txid"],
                tx_timestamp=ts_str,
                event_type="tx_relay"
            )
            obs["synthetic_scenario_label"] = "normal"
            obs_list.append(obs)

        return tx_list, obs_list

    def generate_combined_benchmark_dataset(
        self, 
        normal_count: int = 60, 
        include_anomalies: bool = True
    ) -> Dict[str, Any]:
        """
        Generates a realistic combined benchmark dataset containing normal traffic 
        plus synthetic anomaly scenarios (Peeling-Chain, Mixing, IP Burst).
        """
        base_time = datetime.utcnow() - timedelta(hours=2)
        all_txs = []
        all_obs = []

        # 1. Normal traffic
        txs, obs = self.generate_normal_traffic(count=normal_count, base_time=base_time)
        all_txs.extend(txs)
        all_obs.extend(obs)

        if include_anomalies:
            # 2. Peeling Chain scenario
            peel_txs, peel_obs = self.generate_peeling_chain_scenario(chain_length=6, base_time=base_time + timedelta(minutes=10))
            all_txs.extend(peel_txs)
            all_obs.extend(peel_obs)

            # 3. Mixing pattern scenario
            mix_txs, mix_obs = self.generate_mixing_scenario(mix_count=3, base_time=base_time + timedelta(minutes=30))
            all_txs.extend(mix_txs)
            all_obs.extend(mix_obs)

            # 4. IP Burst anomaly
            burst_txs, burst_obs = self.generate_ip_burst_anomaly(burst_size=12, base_time=base_time + timedelta(minutes=50))
            all_txs.extend(burst_txs)
            all_obs.extend(burst_obs)

        # 5. Deterministic Golden Investigation Case: CASE-001 / TX_GOLDEN_001
        golden_tx = {
            "txid": "TX_GOLDEN_001",
            "timestamp": self._get_timestamp_str(base_time, 15),
            "fee": 15000,
            "size": 250,
            "weight": 1000,
            "block_height": 800000,
            "input_count": 1,
            "output_count": 2,
            "total_input_amount": 500000000,
            "total_output_amount": 499985000,
            "synthetic_scenario_label": "peeling_chain",
            "class_label": 1,
            "dataset_source": "synthetic",
            "inputs": [{
                "prev_txid": "TX_SEED_000",
                "prev_vout_index": 0,
                "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
                "amount": 500000000
            }],
            "outputs": [
                {"address": "12c6DSiU4Rq3P4ZxziKxzrL5LmMBrzjr49", "amount": 450000000, "script_type": "P2WPKH", "is_change_ground_truth": 1},
                {"address": "1HLoD9E4SDFFPDiYfNYnkBLQ85Y51J3Zb1", "amount": 49985000, "script_type": "P2WPKH", "is_change_ground_truth": 0}
            ]
        }
        golden_obs = {
            "obs_id": "OBS_GOLDEN_001",
            "timestamp": golden_tx["timestamp"],
            "src_ip": "198.51.100.45",
            "dst_ip": "203.0.113.12",
            "src_port": 8333,
            "dst_port": 8333,
            "txid": "TX_GOLDEN_001",
            "geo_country": "DE",
            "asn": "AS3320",
            "time_delta": 0.045,
            "network_event_type": "tx_relay",
            "synthetic_scenario_label": "peeling_chain"
        }
        all_txs.append(golden_tx)
        all_obs.append(golden_obs)

        # Sort by timestamp
        all_txs.sort(key=lambda x: x["timestamp"])
        all_obs.sort(key=lambda x: x["timestamp"])

        return {
            "transactions": all_txs,
            "network_observations": all_obs,
            "metadata": {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "total_transactions": len(all_txs),
                "total_network_observations": len(all_obs),
                "scenario_distribution": {
                    "normal": sum(1 for t in all_txs if t["synthetic_scenario_label"] == "normal"),
                    "peeling_chain": sum(1 for t in all_txs if t["synthetic_scenario_label"] == "peeling_chain"),
                    "mixing_pattern": sum(1 for t in all_txs if t["synthetic_scenario_label"] == "mixing_pattern"),
                    "ip_burst_anomaly": sum(1 for t in all_txs if t["synthetic_scenario_label"] == "ip_burst_anomaly"),
                }
            }
        }
