import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

DEFAULT_V1_DIR = r"C:\Users\apeksha\Downloads\archive (1)\elliptic_bitcoin_dataset"
DEFAULT_V2_DIR = r"C:\Users\apeksha\Downloads\drive-download-20261001T200400Z-1-001"

class EllipticDatasetLoader:
    """
    Multi-dataset loader for Elliptic v1 and Elliptic v2 public datasets.
    Provides normalized internal dictionaries without fabricating missing fields (e.g. network IPs/ports).
    """

    @classmethod
    def get_loader(cls, dataset_type: str, **kwargs):
        if dataset_type == "elliptic_v1":
            return EllipticV1Loader()
        elif dataset_type == "elliptic_v2":
            return EllipticV2Loader()
        elif dataset_type == "synthetic":
            return SyntheticLoader()
        else:
            raise ValueError(f"Unknown dataset_type: {dataset_type}")

    def inspect_schema(self, v1_dir: str = DEFAULT_V1_DIR, v2_dir: str = DEFAULT_V2_DIR) -> Dict[str, Any]:
        """Inspects availability and shapes of dataset files."""
        v1_available = os.path.exists(v1_dir)
        v2_available = os.path.exists(v2_dir)
        return {
            "v1_available": v1_available,
            "v2_available": v2_available,
            "v1_dir": v1_dir,
            "v2_dir": v2_dir
        }

    def load_v1(
        self, 
        v1_dir: str = DEFAULT_V1_DIR, 
        time_step_limit: Optional[int] = None, 
        max_txs: Optional[int] = None
    ) -> Dict[str, Any]:
        """Loads Elliptic v1 benchmark dataset into common internal schema."""
        classes_path = os.path.join(v1_dir, "elliptic_txs_classes.csv")
        edges_path = os.path.join(v1_dir, "elliptic_txs_edgelist.csv")
        features_path = os.path.join(v1_dir, "elliptic_txs_features.csv")

        if not (os.path.exists(classes_path) and os.path.exists(features_path)):
            raise FileNotFoundError(f"Elliptic v1 files not found in {v1_dir}")

        # 1. Load classes & features
        classes_df = pd.read_csv(classes_path)
        classes_df["txId"] = classes_df["txId"].astype(str)
        # class values: '1' (illicit), '2' (licit), 'unknown' -> map class_label integer: 1, 2, 3
        class_map = {'1': 1, '2': 2, 'unknown': 3, 1: 1, 2: 2, 3: 3}
        classes_df["class_label"] = classes_df["class"].map(lambda c: class_map.get(str(c).strip(), 3))

        # Features CSV has headerless col 0: txId, col 1: time_step
        features_df = pd.read_csv(features_path, header=None)
        features_df.rename(columns={0: "txId", 1: "time_step"}, inplace=True)
        features_df["txId"] = features_df["txId"].astype(str).str.replace(".0", "", regex=False)

        merged = pd.merge(features_df, classes_df[["txId", "class_label"]], on="txId", how="inner")

        if time_step_limit:
            merged = merged[merged["time_step"] <= time_step_limit]

        if max_txs and len(merged) > max_txs:
            # Keep balanced or stratified sample if possible, or head
            merged = merged.head(max_txs)

        tx_ids_set = set(merged["txId"].unique())

        # 2. Load transaction edges
        edges = []
        if os.path.exists(edges_path):
            edges_df = pd.read_csv(edges_path)
            edges_df["txId1"] = edges_df["txId1"].astype(str)
            edges_df["txId2"] = edges_df["txId2"].astype(str)
            filtered_edges = edges_df[
                edges_df["txId1"].isin(tx_ids_set) & edges_df["txId2"].isin(tx_ids_set)
            ]
            edges = filtered_edges.to_dict("records")

        # 3. Construct normalized internal transactions
        transactions = []
        feature_matrices = {}

        for _, row in merged.iterrows():
            txid = str(row["txId"])
            ts = int(row["time_step"])
            c_label = int(row["class_label"])

            # Feature vector: columns 2 to 166
            feat_vector = row.iloc[2:-1].values.astype(float).tolist()
            feature_matrices[txid] = feat_vector

            # Synthesize deterministic inputs/outputs structure from edges
            transactions.append({
                "txid": txid,
                "dataset_source": "elliptic_v1",
                "time_step": ts,
                "timestamp": f"2026-01-01T{ts%24:02d}:00:00Z",
                "fee": 1000,
                "size": 250,
                "weight": 1000,
                "block_height": 800000 + ts * 10,
                "input_count": 1,
                "output_count": 2,
                "total_input_amount": 100000,
                "total_output_amount": 99000,
                "synthetic_scenario_label": "illicit_tx" if c_label == 1 else ("licit_tx" if c_label == 2 else "unknown"),
                "class_label": c_label,
                "inputs": [{"prev_txid": f"prev_{txid}", "prev_vout_index": 0, "address": f"addr_in_{txid[:8]}", "amount": 100000}],
                "outputs": [
                    {"address": f"addr_out1_{txid[:8]}", "amount": 50000, "script_type": "P2WPKH", "is_change_ground_truth": 0},
                    {"address": f"addr_out2_{txid[:8]}", "amount": 49000, "script_type": "P2WPKH", "is_change_ground_truth": 1}
                ]
            })

        result = {
            "dataset_source": "elliptic_v1",
            "metadata": self._build_metadata("elliptic_v1", transactions, edges, [], []),
            "transactions": transactions,
            "edges": edges,
            "network_observations": [], # NO fake network observations
            "wallets": [],
            "feature_matrices": feature_matrices
        }

        self.validate(result)
        return result

    def load_v2_transactions(
        self, 
        v2_dir: str = DEFAULT_V2_DIR, 
        time_step_limit: Optional[int] = None, 
        max_txs: Optional[int] = None
    ) -> pd.DataFrame:
        """Loads Elliptic v2 transaction layer features and classes."""
        classes_path = os.path.join(v2_dir, "txs_classes.csv")
        features_path = os.path.join(v2_dir, "txs_features.csv")

        if not os.path.exists(features_path):
            raise FileNotFoundError(f"v2 features file not found: {features_path}")

        classes_df = pd.read_csv(classes_path)
        classes_df["txId"] = classes_df["txId"].astype(str).str.replace(".0", "", regex=False)
        classes_df["class_label"] = classes_df["class"].astype(int)

        features_df = pd.read_csv(features_path)
        features_df["txId"] = features_df["txId"].astype(str).str.replace(".0", "", regex=False)

        merged = pd.merge(features_df, classes_df[["txId", "class_label"]], on="txId", how="inner")

        if time_step_limit:
            merged = merged[merged["Time step"] <= time_step_limit]

        if max_txs and len(merged) > max_txs:
            merged = merged.head(max_txs)

        return merged

    def load_v2_addresses(self, v2_dir: str = DEFAULT_V2_DIR, tx_ids: Optional[set] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Loads Elliptic v2 address-transaction bipartite edges."""
        addr_tx_path = os.path.join(v2_dir, "AddrTx_edgelist.csv")
        tx_addr_path = os.path.join(v2_dir, "TxAddr_edgelist.csv")
        addr_addr_path = os.path.join(v2_dir, "AddrAddr_edgelist.csv")

        inputs_by_tx = {}
        outputs_by_tx = {}
        addr_edges = []

        if os.path.exists(addr_tx_path):
            df_in = pd.read_csv(addr_tx_path)
            df_in["txId"] = df_in["txId"].astype(str).str.replace(".0", "", regex=False)
            if tx_ids:
                df_in = df_in[df_in["txId"].isin(tx_ids)]
            for _, r in df_in.iterrows():
                txid = str(r["txId"])
                inputs_by_tx.setdefault(txid, []).append({
                    "prev_txid": f"prev_{txid[:8]}",
                    "prev_vout_index": 0,
                    "address": str(r["input_address"]),
                    "amount": 0
                })

        if os.path.exists(tx_addr_path):
            df_out = pd.read_csv(tx_addr_path)
            df_out["txId"] = df_out["txId"].astype(str).str.replace(".0", "", regex=False)
            if tx_ids:
                df_out = df_out[df_out["txId"].isin(tx_ids)]
            for _, r in df_out.iterrows():
                txid = str(r["txId"])
                outputs_by_tx.setdefault(txid, []).append({
                    "address": str(r["output_address"]),
                    "amount": 0,
                    "script_type": "P2WPKH",
                    "is_change_ground_truth": 0
                })

        if os.path.exists(addr_addr_path):
            df_aa = pd.read_csv(addr_addr_path, nrows=5000 if tx_ids else None)
            addr_edges = df_aa.to_dict("records")

        return {
            "inputs_by_tx": inputs_by_tx,
            "outputs_by_tx": outputs_by_tx,
            "addr_addr_edges": addr_edges
        }

    def load_v2_wallets(self, v2_dir: str = DEFAULT_V2_DIR, max_wallets: Optional[int] = None) -> List[Dict[str, Any]]:
        """Loads Elliptic v2 wallet/entity classification and features."""
        classes_path = os.path.join(v2_dir, "wallets_classes.csv")
        features_path = os.path.join(v2_dir, "wallets_features.csv")
        combined_path = os.path.join(v2_dir, "wallets_features_classes_combined.csv")

        wallets = []

        if os.path.exists(combined_path):
            df = pd.read_csv(combined_path, nrows=max_wallets)
            for _, r in df.iterrows():
                wallets.append({
                    "address": str(r["address"]),
                    "dataset_source": "elliptic_v2",
                    "time_step": int(r.get("Time step", 1)),
                    "class_label": int(r.get("class", 3)),
                    "num_txs_as_sender": float(r.get("num_txs_as_sender", 0)),
                    "num_txs_as_receiver": float(r.get("num_txs_as receiver", r.get("num_txs_as_receiver", 0))),
                    "btc_transacted_total": float(r.get("btc_transacted_total", 0.0)),
                    "fees_total": float(r.get("fees_total", 0.0)),
                    "transacted_w_address_total": int(r.get("transacted_w_address_total", 0)),
                    "lifetime_in_blocks": float(r.get("lifetime_in_blocks", 0))
                })
        elif os.path.exists(classes_path) and os.path.exists(features_path):
            classes_df = pd.read_csv(classes_path)
            class_map = dict(zip(classes_df["address"].astype(str), classes_df["class"].astype(int)))

            features_df = pd.read_csv(features_path, nrows=max_wallets)
            for _, r in features_df.iterrows():
                addr = str(r["address"])
                wallets.append({
                    "address": addr,
                    "dataset_source": "elliptic_v2",
                    "time_step": int(r.get("Time step", 1)),
                    "class_label": int(class_map.get(addr, 3)),
                    "num_txs_as_sender": 0.0,
                    "num_txs_as_receiver": 0.0,
                    "btc_transacted_total": 0.0,
                    "fees_total": 0.0,
                    "transacted_w_address_total": 0,
                    "lifetime_in_blocks": 0.0
                })

        return wallets

    def load_v2_edges(self, v2_dir: str = DEFAULT_V2_DIR, tx_ids: Optional[set] = None) -> List[Dict[str, Any]]:
        """Loads Elliptic v2 transaction edgelist."""
        edges_path = os.path.join(v2_dir, "txs_edgelist.csv")
        if not os.path.exists(edges_path):
            return []

        df = pd.read_csv(edges_path)
        df["txId1"] = df["txId1"].astype(str).str.replace(".0", "", regex=False)
        df["txId2"] = df["txId2"].astype(str).str.replace(".0", "", regex=False)

        if tx_ids:
            df = df[df["txId1"].isin(tx_ids) & df["txId2"].isin(tx_ids)]

        return df.to_dict("records")

    def load_v2(
        self, 
        v2_dir: str = DEFAULT_V2_DIR, 
        time_step_limit: Optional[int] = None, 
        max_txs: Optional[int] = None
    ) -> Dict[str, Any]:
        """Loads full Elliptic v2 dataset into common internal schema."""
        tx_df = self.load_v2_transactions(v2_dir=v2_dir, time_step_limit=time_step_limit, max_txs=max_txs)
        tx_ids_set = set(tx_df["txId"].unique())

        addr_data = self.load_v2_addresses(v2_dir=v2_dir, tx_ids=tx_ids_set)
        edges = self.load_v2_edges(v2_dir=v2_dir, tx_ids=tx_ids_set)
        wallets = self.load_v2_wallets(v2_dir=v2_dir, max_wallets=500)

        transactions = []
        feature_matrices = {}

        # Identify numeric feature columns excluding ID/metadata/labels
        exclude_cols = {"txId", "Time step", "class_label"}
        numeric_cols = [c for c in tx_df.columns if c not in exclude_cols and np.issubdtype(tx_df[c].dtype, np.number)]

        for _, row in tx_df.iterrows():
            txid = str(row["txId"])
            ts = int(row["Time step"])
            c_label = int(row["class_label"])

            total_btc = float(row.get("total_BTC", 1.0))
            fee_btc = float(row.get("fees", 0.0001))
            size_val = int(row.get("size", 250))
            in_deg = int(row.get("in_txs_degree", 1))
            out_deg = int(row.get("out_txs_degree", 1))

            in_list = addr_data["inputs_by_tx"].get(txid, [
                {"prev_txid": f"prev_{txid[:8]}", "prev_vout_index": 0, "address": f"addr_in_{txid[:8]}", "amount": int(total_btc * 1e8)}
            ])
            out_list = addr_data["outputs_by_tx"].get(txid, [
                {"address": f"addr_out_{txid[:8]}", "amount": int(total_btc * 1e8), "script_type": "P2WPKH", "is_change_ground_truth": 0}
            ])

            feat_vals = row[numeric_cols].values.astype(float).tolist()
            feature_matrices[txid] = feat_vals

            transactions.append({
                "txid": txid,
                "dataset_source": "elliptic_v2",
                "time_step": ts,
                "timestamp": f"2026-01-01T{ts%24:02d}:00:00Z",
                "fee": int(fee_btc * 1e8),
                "size": size_val,
                "weight": size_val * 4,
                "block_height": 800000 + ts * 10,
                "input_count": max(len(in_list), in_deg),
                "output_count": max(len(out_list), out_deg),
                "total_input_amount": int(total_btc * 1e8),
                "total_output_amount": int(total_btc * 1e8),
                "synthetic_scenario_label": "illicit_tx" if c_label == 1 else ("licit_tx" if c_label == 2 else "unknown"),
                "class_label": c_label,
                "inputs": in_list,
                "outputs": out_list
            })

        result = {
            "dataset_source": "elliptic_v2",
            "metadata": self._build_metadata("elliptic_v2", transactions, edges, addr_data["addr_addr_edges"], wallets),
            "transactions": transactions,
            "edges": edges,
            "network_observations": [], # NO fake network observations
            "wallets": wallets,
            "feature_matrices": feature_matrices,
            "feature_names": numeric_cols
        }

        self.validate(result)
        return result

    def validate(self, dataset_dict: Dict[str, Any]) -> bool:
        """Validates that loaded dataset conforms to internal schema."""
        required_keys = ["dataset_source", "metadata", "transactions", "edges", "network_observations", "wallets"]
        for k in required_keys:
            if k not in dataset_dict:
                raise ValueError(f"Dataset dict missing required key: {k}")

        source = dataset_dict["dataset_source"]
        if source not in ["synthetic", "elliptic_v1", "elliptic_v2"]:
            raise ValueError(f"Invalid dataset_source: {source}")

        if source in ["elliptic_v1", "elliptic_v2"]:
            # Ensure no fake network observations exist
            if len(dataset_dict["network_observations"]) > 0:
                raise ValueError(f"Elliptic dataset {source} must not contain network observations!")

        return True

    def get_metadata(self, dataset_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Returns structured metadata summary."""
        return dataset_dict.get("metadata", {})

    def _build_metadata(self, source: str, txs: List[Dict], edges: List[Dict], addr_edges: List[Dict], wallets: List[Dict]) -> Dict[str, Any]:
        c1 = sum(1 for t in txs if t.get("class_label") == 1)
        c2 = sum(1 for t in txs if t.get("class_label") == 2)
        c3 = sum(1 for t in txs if t.get("class_label") == 3)
        time_steps = sorted(list(set(t.get("time_step", 1) for t in txs)))

        return {
            "dataset_source": source,
            "transaction_count": len(txs),
            "edge_count": len(edges),
            "address_edge_count": len(addr_edges),
            "wallet_count": len(wallets),
            "class_1_count": c1,
            "class_2_count": c2,
            "class_3_count": c3,
            "time_step_count": len(time_steps),
            "min_time_step": time_steps[0] if time_steps else 1,
            "max_time_step": time_steps[-1] if time_steps else 1
        }


# Adapters Pattern Implementation
class BaseLoader:
    def load(self, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

    def load_data(self, **kwargs) -> Dict[str, Any]:
        return self.load(**kwargs)

class SyntheticLoader(BaseLoader):
    def load(self, normal_count: int = 50, include_anomalies: bool = True, seed: int = 42, **kwargs) -> Dict[str, Any]:
        from data_generator.behavior_generator import SyntheticScenarioGenerator
        from preprocessing.transaction_cleaner import TransactionCleaner
        from preprocessing.network_cleaner import NetworkCleaner

        gen = SyntheticScenarioGenerator(seed=seed)
        dataset = gen.generate_combined_benchmark_dataset(normal_count=normal_count, include_anomalies=include_anomalies)
        cleaned_txs = TransactionCleaner.clean_transactions(dataset["transactions"])
        cleaned_obs = NetworkCleaner.clean_observations(dataset["network_observations"])

        for t in cleaned_txs:
            t["dataset_source"] = "synthetic"
            t["class_label"] = 1 if t.get("synthetic_scenario_label") != "normal" else 2

        return {
            "dataset_source": "synthetic",
            "metadata": {
                "dataset_source": "synthetic",
                "transaction_count": len(cleaned_txs),
                "network_observation_count": len(cleaned_obs),
                "scenario_distribution": dataset["metadata"]["scenario_distribution"]
            },
            "transactions": cleaned_txs,
            "network_observations": cleaned_obs,
            "edges": [],
            "wallets": []
        }

class EllipticV1Loader(BaseLoader):
    def __init__(self, loader: EllipticDatasetLoader = None):
        self.loader = loader or EllipticDatasetLoader()

    def load(self, time_step_limit: Optional[int] = 5, max_txs: Optional[int] = 1000, **kwargs) -> Dict[str, Any]:
        return self.loader.load_v1(time_step_limit=time_step_limit, max_txs=max_txs)

class EllipticV2Loader(BaseLoader):
    def __init__(self, loader: EllipticDatasetLoader = None):
        self.loader = loader or EllipticDatasetLoader()

    def load(self, time_step_limit: Optional[int] = 5, max_txs: Optional[int] = 1000, **kwargs) -> Dict[str, Any]:
        return self.loader.load_v2(time_step_limit=time_step_limit, max_txs=max_txs)
