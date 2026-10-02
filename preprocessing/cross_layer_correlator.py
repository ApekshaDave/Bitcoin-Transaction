from typing import List, Dict, Any, Set

class CrossLayerCorrelator:
    """
    Cross-Layer Correlation Engine.
    Correlates Network Layer observations (timestamp, src_ip, dst_ip, ports) 
    with Blockchain Layer transactions (TXID, inputs, outputs, amounts, fees).
    
    Treats cross-layer linkages strictly as evidence/observation associations, 
    not proof of real-world identity.
    """
    def __init__(
        self, 
        transactions: List[Dict[str, Any]], 
        network_observations: List[Dict[str, Any]]
    ):
        self.transactions_by_txid: Dict[str, Dict[str, Any]] = {
            tx["txid"]: tx for tx in transactions
        }
        self.observations_by_txid: Dict[str, List[Dict[str, Any]]] = {}
        self.observations_by_ip: Dict[str, List[Dict[str, Any]]] = {}
        self.txids_by_ip: Dict[str, Set[str]] = {}
        self.addresses_by_ip: Dict[str, Set[str]] = {}

        self._index_observations(network_observations)

    def _index_observations(self, observations: List[Dict[str, Any]]) -> None:
        for obs in observations:
            txid = obs["txid"]
            ip = obs["src_ip"]

            # Index by TXID
            if txid not in self.observations_by_txid:
                self.observations_by_txid[txid] = []
            self.observations_by_txid[txid].append(obs)

            # Index by IP
            if ip not in self.observations_by_ip:
                self.observations_by_ip[ip] = []
            self.observations_by_ip[ip].append(obs)

            if ip not in self.txids_by_ip:
                self.txids_by_ip[ip] = set()
            self.txids_by_ip[ip].add(txid)

            # Link IP to participant addresses in associated transactions
            if txid in self.transactions_by_txid:
                tx = self.transactions_by_txid[txid]
                if ip not in self.addresses_by_ip:
                    self.addresses_by_ip[ip] = set()
                
                for inp in tx.get("inputs", []):
                    if "address" in inp:
                        self.addresses_by_ip[ip].add(inp["address"])
                for out in tx.get("outputs", []):
                    if "address" in out:
                        self.addresses_by_ip[ip].add(out["address"])

    def get_network_observations_for_tx(self, txid: str) -> List[Dict[str, Any]]:
        """Returns all network observations linked to a TXID."""
        return self.observations_by_txid.get(txid, [])

    def get_transactions_for_ip(self, ip: str) -> List[Dict[str, Any]]:
        """Returns all blockchain transactions linked to a network IP address."""
        txids = self.txids_by_ip.get(ip, set())
        return [self.transactions_by_txid[txid] for txid in txids if txid in self.transactions_by_txid]

    def get_addresses_for_ip(self, ip: str) -> List[str]:
        """Returns all wallet addresses participating in transactions linked to an IP."""
        return sorted(list(self.addresses_by_ip.get(ip, set())))

    def get_ips_for_address(self, address: str) -> List[str]:
        """Returns all IPs linked to transactions containing a specific address."""
        linked_ips = set()
        for ip, addrs in self.addresses_by_ip.items():
            if address in addrs:
                linked_ips.add(ip)
        return sorted(list(linked_ips))

    def get_correlation_summary(self) -> Dict[str, Any]:
        """Generates cross-layer correlation summary metrics."""
        return {
            "total_correlated_transactions": len(self.observations_by_txid),
            "total_unique_ips": len(self.observations_by_ip),
            "ip_to_tx_distribution": {
                ip: len(txids) for ip, txids in self.txids_by_ip.items()
            },
            "ip_to_address_distribution": {
                ip: len(addrs) for ip, addrs in self.addresses_by_ip.items()
            }
        }
