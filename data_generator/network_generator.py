import random
import hashlib
from typing import Dict, Any, List
from data_generator.geoip_generator import GeoIPASNEnricher

class NetworkDataGenerator:
    """
    Synthetic Network Observation Generator.
    Correlates network-layer P2P observations (IP, ports, timing, GeoIP, ASN)
    with blockchain transaction TXIDs.
    """
    def __init__(self, enricher: GeoIPASNEnricher = None, seed: int = 42):
        random.seed(seed)
        self.enricher = enricher or GeoIPASNEnricher()
        self.ip_pool: List[str] = [self._generate_ip() for _ in range(50)]
        self.obs_counter = 0

    def _generate_ip(self) -> str:
        """Generates a synthetic IPv4 address (excluding private RFC1918 ranges)."""
        b1 = random.choice([x for x in range(1, 223) if x not in [10, 127, 172, 192]])
        b2 = random.randint(0, 255)
        b3 = random.randint(0, 255)
        b4 = random.randint(1, 254)
        return f"{b1}.{b2}.{b3}.{b4}"

    def generate_observation_for_tx(
        self,
        txid: str,
        tx_timestamp: str,
        override_src_ip: str = None,
        override_dst_ip: str = None,
        event_type: str = "tx_relay"
    ) -> Dict[str, Any]:
        """
        Generates a synthetic P2P network observation associated with a TXID.
        """
        self.obs_counter += 1
        obs_id = f"obs_{self.obs_counter}_{hashlib.md5(txid.encode('utf-8')).hexdigest()[:8]}"

        src_ip = override_src_ip or random.choice(self.ip_pool)
        dst_ip = override_dst_ip or random.choice([ip for ip in self.ip_pool if ip != src_ip])
        
        src_port = random.randint(1024, 65535)
        dst_port = 8333  # Standard Bitcoin mainnet P2P port
        
        time_delta = round(random.uniform(0.05, 1.5), 3)  # Propagation delay in seconds
        country, asn = self.enricher.lookup(src_ip)

        return {
            "obs_id": obs_id,
            "timestamp": tx_timestamp,
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "src_port": src_port,
            "dst_port": dst_port,
            "txid": txid,
            "geo_country": country,
            "asn": asn,
            "time_delta": time_delta,
            "network_event_type": event_type
        }
