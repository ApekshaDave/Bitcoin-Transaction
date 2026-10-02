import sqlite3
import json
import os
from typing import List, Dict, Any, Optional, Tuple

DB_FILE = os.path.join(os.path.dirname(__file__), "bitcoin_monitor.db")

class MemoryConnectionContext:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def __enter__(self) -> sqlite3.Connection:
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()

class DatabaseManager:
    """
    Manages SQLite database storage for:
    - transactions & tx_inputs (with prev_txid) & tx_outputs (with is_change_ground_truth)
    - network_observations
    - entity_clusters & entity_address_mapping
    - alerts (with evidence_json)
    """
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self._shared_conn = None
        if self.db_path == ":memory:":
            self._shared_conn = sqlite3.connect("file:memdb1?mode=memory&cache=shared", uri=True, check_same_thread=False)
            self._shared_conn.row_factory = sqlite3.Row
        self.init_db()

    def get_connection(self):
        if self.db_path == ":memory:":
            return MemoryConnectionContext(self._shared_conn)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Initializes database table schemas."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Transactions
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                txid TEXT PRIMARY KEY,
                timestamp TEXT,
                fee INTEGER,
                size INTEGER,
                weight INTEGER,
                block_height INTEGER,
                input_count INTEGER,
                output_count INTEGER,
                total_input_amount INTEGER,
                total_output_amount INTEGER,
                synthetic_scenario_label TEXT,
                dataset_source TEXT DEFAULT 'synthetic',
                class_label INTEGER DEFAULT 3
            )
            """)

            # Inputs (including prev_txid and prev_vout_index)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tx_inputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                txid TEXT,
                prev_txid TEXT,
                prev_vout_index INTEGER,
                address TEXT,
                amount INTEGER,
                FOREIGN KEY(txid) REFERENCES transactions(txid)
            )
            """)

            # Outputs (including is_change_ground_truth)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tx_outputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                txid TEXT,
                address TEXT,
                amount INTEGER,
                script_type TEXT,
                is_change_ground_truth INTEGER,
                FOREIGN KEY(txid) REFERENCES transactions(txid)
            )
            """)

            # Network Observations
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS network_observations (
                obs_id TEXT PRIMARY KEY,
                timestamp TEXT,
                src_ip TEXT,
                dst_ip TEXT,
                src_port INTEGER,
                dst_port INTEGER,
                txid TEXT,
                geo_country TEXT,
                asn TEXT,
                time_delta REAL,
                network_event_type TEXT,
                FOREIGN KEY(txid) REFERENCES transactions(txid)
            )
            """)

            # Entity Clusters
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity_clusters (
                entity_id TEXT PRIMARY KEY,
                cluster_algorithm TEXT,
                created_at TEXT,
                address_count INTEGER
            )
            """)

            # Entity Address Mapping
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity_address_mapping (
                entity_id TEXT,
                address TEXT PRIMARY KEY,
                confidence REAL,
                FOREIGN KEY(entity_id) REFERENCES entity_clusters(entity_id)
            )
            """)

            # Wallets / Entity Unique Addresses Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS wallets (
                address TEXT,
                dataset_source TEXT DEFAULT 'elliptic_v2',
                time_step INTEGER DEFAULT 1,
                class_label INTEGER DEFAULT 3,
                num_txs_as_sender REAL DEFAULT 0,
                num_txs_as_receiver REAL DEFAULT 0,
                btc_transacted_total REAL DEFAULT 0.0,
                fees_total REAL DEFAULT 0.0,
                transacted_w_address_total INTEGER DEFAULT 0,
                lifetime_in_blocks REAL DEFAULT 0,
                risk_score REAL DEFAULT 0.0,
                PRIMARY KEY(address, dataset_source)
            )
            """)

            # Wallet Temporal Features Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS wallet_temporal_features (
                address TEXT,
                dataset_source TEXT DEFAULT 'elliptic_v2',
                time_step INTEGER,
                class_label INTEGER DEFAULT 3,
                num_txs_as_sender REAL DEFAULT 0,
                num_txs_as_receiver REAL DEFAULT 0,
                btc_transacted_total REAL DEFAULT 0.0,
                fees_total REAL DEFAULT 0.0,
                transacted_w_address_total INTEGER DEFAULT 0,
                lifetime_in_blocks REAL DEFAULT 0,
                risk_score REAL DEFAULT 0.0,
                PRIMARY KEY(address, dataset_source, time_step)
            )
            """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_wallets_ds ON wallets(dataset_source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_wallet_temp_ds_ts ON wallet_temporal_features(dataset_source, time_step)")

            # Dataset Metadata Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS dataset_metadata (
                dataset_id TEXT PRIMARY KEY,
                dataset_source TEXT,
                dataset_version TEXT,
                dataset_name TEXT,
                loaded_at TEXT,
                transaction_count INTEGER,
                address_count INTEGER,
                wallet_count INTEGER,
                edge_count INTEGER,
                class_1_count INTEGER,
                class_2_count INTEGER,
                class_3_count INTEGER,
                time_step_count INTEGER,
                status TEXT
            )
            """)

            # Alerts
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                target_type TEXT,
                target_id TEXT,
                risk_score REAL,
                confidence REAL,
                alert_type TEXT,
                created_at TEXT,
                evidence_json TEXT,
                dataset_source TEXT DEFAULT 'synthetic'
            )
            """)

            # Migration check for existing SQLite files
            cursor.execute("PRAGMA table_info(transactions)")
            existing_cols = [row[1] for row in cursor.fetchall()]
            if "dataset_source" not in existing_cols:
                cursor.execute("ALTER TABLE transactions ADD COLUMN dataset_source TEXT DEFAULT 'synthetic'")
            if "class_label" not in existing_cols:
                cursor.execute("ALTER TABLE transactions ADD COLUMN class_label INTEGER DEFAULT 3")

            cursor.execute("PRAGMA table_info(alerts)")
            alert_cols = [row[1] for row in cursor.fetchall()]
            if "dataset_source" not in alert_cols:
                cursor.execute("ALTER TABLE alerts ADD COLUMN dataset_source TEXT DEFAULT 'synthetic'")

            conn.commit()

    def clear_all_tables(self) -> None:
        """Cleans all existing records."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for tbl in ["alerts", "entity_address_mapping", "entity_clusters", "network_observations", "tx_outputs", "tx_inputs", "transactions", "wallets", "wallet_temporal_features", "dataset_metadata"]:
                cursor.execute(f"DELETE FROM {tbl}")
            conn.commit()

    def save_transactions_and_observations(
        self, 
        transactions: List[Dict[str, Any]], 
        observations: List[Dict[str, Any]],
        wallets: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Persists transactions, inputs, outputs, network observations, wallets, and dataset metadata."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for tx in transactions:
                cursor.execute("""
                INSERT OR REPLACE INTO transactions 
                (txid, timestamp, fee, size, weight, block_height, input_count, output_count, total_input_amount, total_output_amount, synthetic_scenario_label, dataset_source, class_label)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tx["txid"], tx.get("timestamp"), tx.get("fee", 0), tx.get("size", 250),
                    tx.get("weight", 1000), tx.get("block_height", 800000), tx.get("input_count", 0),
                    tx.get("output_count", 0), tx.get("total_input_amount", 0), tx.get("total_output_amount", 0),
                    tx.get("synthetic_scenario_label", "normal"),
                    tx.get("dataset_source", "synthetic"),
                    tx.get("class_label", 3)
                ))

                for inp in tx.get("inputs", []):
                    cursor.execute("""
                    INSERT INTO tx_inputs (txid, prev_txid, prev_vout_index, address, amount)
                    VALUES (?, ?, ?, ?, ?)
                    """, (tx["txid"], inp.get("prev_txid"), inp.get("prev_vout_index"), inp.get("address"), inp.get("amount", 0)))

                for out in tx.get("outputs", []):
                    cursor.execute("""
                    INSERT INTO tx_outputs (txid, address, amount, script_type, is_change_ground_truth)
                    VALUES (?, ?, ?, ?, ?)
                    """, (tx["txid"], out.get("address"), out.get("amount", 0), out.get("script_type", "P2WPKH"), out.get("is_change_ground_truth", 0)))

            for obs in observations:
                cursor.execute("""
                INSERT OR REPLACE INTO network_observations
                (obs_id, timestamp, src_ip, dst_ip, src_port, dst_port, txid, geo_country, asn, time_delta, network_event_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    obs["obs_id"], obs.get("timestamp"), obs.get("src_ip"), obs.get("dst_ip"),
                    obs.get("src_port", 8333), obs.get("dst_port", 8333), obs["txid"],
                    obs.get("geo_country", "UNKNOWN"), obs.get("asn", "UNKNOWN"),
                    obs.get("time_delta", 0.0), obs.get("network_event_type", "tx_relay")
                ))

            if wallets:
                for w in wallets:
                    cursor.execute("""
                    INSERT OR REPLACE INTO wallets
                    (address, dataset_source, time_step, class_label, num_txs_as_sender, num_txs_as_receiver, btc_transacted_total, fees_total, transacted_w_address_total, lifetime_in_blocks, risk_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        w["address"], w.get("dataset_source", "elliptic_v2"), w.get("time_step", 1),
                        w.get("class_label", 3), w.get("num_txs_as_sender", 0.0), w.get("num_txs_as_receiver", 0.0),
                        w.get("btc_transacted_total", 0.0), w.get("fees_total", 0.0), w.get("transacted_w_address_total", 0),
                        w.get("lifetime_in_blocks", 0.0), w.get("risk_score", 0.0)
                    ))

            if metadata:
                import datetime
                cursor.execute("""
                INSERT OR REPLACE INTO dataset_metadata
                (dataset_id, dataset_source, dataset_version, dataset_name, loaded_at, transaction_count, address_count, wallet_count, edge_count, class_1_count, class_2_count, class_3_count, time_step_count, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"meta-{metadata.get('dataset_source', 'synthetic')}",
                    metadata.get("dataset_source", "synthetic"),
                    "1.0",
                    metadata.get("dataset_source", "synthetic").upper(),
                    datetime.datetime.utcnow().isoformat() + "Z",
                    metadata.get("transaction_count", 0),
                    metadata.get("address_edge_count", 0),
                    metadata.get("wallet_count", 0),
                    metadata.get("edge_count", 0),
                    metadata.get("class_1_count", 0),
                    metadata.get("class_2_count", 0),
                    metadata.get("class_3_count", 0),
                    metadata.get("time_step_count", 1),
                    "active"
                ))

            conn.commit()

    def save_alerts(self, alerts: List[Dict[str, Any]], dataset_source: str = "synthetic") -> None:
        """Persists alerts into SQLite."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for alt in alerts:
                ev_str = json.dumps(alt.get("evidence", {}))
                d_source = alt.get("dataset_source", dataset_source)
                cursor.execute("""
                INSERT OR REPLACE INTO alerts
                (alert_id, target_type, target_id, risk_score, confidence, alert_type, created_at, evidence_json, dataset_source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alt["alert_id"], alt.get("target_type", "TRANSACTION"), alt["target_id"],
                    alt.get("risk_score", 0.0), alt.get("confidence", 0.5), alt.get("alert_type", "ANOMALY"),
                    alt.get("created_at", "N/A"), ev_str, d_source
                ))
            conn.commit()

    def save_wallets(self, wallets: List[Dict[str, Any]], dataset_source: str = "elliptic_v2") -> None:
        """Stores or updates wallet records in SQLite database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for w in wallets:
                cursor.execute("""
                INSERT OR REPLACE INTO wallets (
                    address, dataset_source, time_step, class_label,
                    num_txs_as_sender, num_txs_as_receiver, btc_transacted_total,
                    fees_total, transacted_w_address_total, lifetime_in_blocks, risk_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(w.get("address", "")),
                    w.get("dataset_source", dataset_source),
                    int(w.get("time_step", 1)),
                    int(w.get("class_label", 3)),
                    float(w.get("num_txs_as_sender", 0)),
                    float(w.get("num_txs_as_receiver", 0)),
                    float(w.get("btc_transacted_total", 0.0)),
                    float(w.get("fees_total", 0.0)),
                    int(w.get("transacted_w_address_total", 0)),
                    float(w.get("lifetime_in_blocks", 0)),
                    float(w.get("risk_score", 0.0))
                ))
            conn.commit()

    def get_all_transactions(self) -> List[Dict[str, Any]]:
        """Retrieves all transactions with inputs and outputs."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions")
            tx_rows = [dict(r) for r in cursor.fetchall()]
            
            for tx in tx_rows:
                txid = tx["txid"]
                tx["tx_id"] = txid
                tx["tx_hash"] = f"0x{hash(txid) % (16**64):064x}" if not txid.startswith("0x") else txid
                
                cursor.execute("SELECT prev_txid, prev_vout_index, address, amount FROM tx_inputs WHERE txid = ?", (txid,))
                tx["inputs"] = [dict(r) for r in cursor.fetchall()]
                tx["input_addresses"] = [inp["address"] for inp in tx["inputs"] if inp.get("address")]
                
                cursor.execute("SELECT address, amount, script_type, is_change_ground_truth FROM tx_outputs WHERE txid = ?", (txid,))
                tx["outputs"] = [dict(r) for r in cursor.fetchall()]
                tx["output_addresses"] = [out["address"] for out in tx["outputs"] if out.get("address")]
                
                tx["amount_btc"] = float(tx.get("total_input_amount", 0)) / 1e8 if tx.get("total_input_amount") else 1.0
                tx["fee_btc"] = float(tx.get("fee", 0)) / 1e8
                
            return tx_rows

    def get_all_observations(self) -> List[Dict[str, Any]]:
        """Retrieves all network observations."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM network_observations")
            obs_rows = [dict(r) for r in cursor.fetchall()]
            for o in obs_rows:
                o["associated_tx_id"] = o.get("txid")
                o["observation_id"] = o.get("obs_id")
                o["node_ip"] = o.get("src_ip")
            return obs_rows

    def get_all_alerts(self) -> List[Dict[str, Any]]:
        """Retrieves all stored alerts."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM alerts ORDER BY risk_score DESC")
            alerts = []
            for r in cursor.fetchall():
                d = dict(r)
                if d.get("evidence_json"):
                    try:
                        d["evidence"] = json.loads(d["evidence_json"])
                    except Exception:
                        d["evidence"] = {}
                alerts.append(d)
            return alerts

    def load_latest_data(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        """Loads latest transactions, network observations, wallets, and dataset metadata."""
        txs = self.get_all_transactions()
        obs = self.get_all_observations()
        
        wallets = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM wallets")
            wallets = [dict(r) for r in cursor.fetchall()]

            cursor.execute("SELECT * FROM dataset_metadata ORDER BY loaded_at DESC LIMIT 1")
            meta_row = cursor.fetchone()
            meta = dict(meta_row) if meta_row else {}

        return txs, obs, wallets, meta


