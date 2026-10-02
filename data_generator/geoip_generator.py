import hashlib
from typing import Dict, Tuple, Optional

class GeoIPASNEnricher:
    """
    GeoIP & ASN Enrichment Provider supporting:
    - Mode 1: Local GeoIP/ASN Database lookup
    - Mode 2: Synthetic Fallback generator (deterministic mapping based on IP hash)
    
    Operates strictly offline without external web dependencies.
    """
    def __init__(self, local_db: Optional[Dict[str, Tuple[str, str]]] = None):
        # Local database mapping IP or CIDR -> (Country Code, ASN)
        self.local_db: Dict[str, Tuple[str, str]] = local_db or {}
        
        # Synthetic fallback pools
        self._fallback_countries = ["US", "DE", "JP", "CN", "GB", "NL", "SG", "BR", "CA", "IN", "FR", "RU", "AU", "KR", "CH"]
        self._fallback_asns = [
            "AS15169 Google LLC",
            "AS16509 Amazon.com, Inc.",
            "AS7922 Comcast Cable",
            "AS3356 Level 3 Parent, LLC",
            "AS13335 Cloudflare, Inc.",
            "AS24940 Hetzner Online GmbH",
            "AS63949 Linode, LLC",
            "AS14061 DigitalOcean, LLC",
            "AS4837 CHINA UNICOM China169 Backbone",
            "AS9808 China Mobile Communications Group"
        ]

    def register_local_ip(self, ip: str, country: str, asn: str) -> None:
        """Register a local GeoIP/ASN entry into Mode 1 database."""
        self.local_db[ip] = (country, asn)

    def lookup(self, ip: str) -> Tuple[str, str]:
        """
        Lookup GeoIP Country and ASN for a given IPv4/IPv6 address.
        Attempts Mode 1 (Local DB) first, falling back to Mode 2 (Synthetic Fallback).
        """
        # Mode 1: Local DB lookup
        if ip in self.local_db:
            return self.local_db[ip]
        
        # Mode 2: Deterministic Synthetic Fallback based on IP hash
        ip_hash = int(hashlib.sha256(ip.encode('utf-8')).hexdigest(), 16)
        country = self._fallback_countries[ip_hash % len(self._fallback_countries)]
        asn = self._fallback_asns[(ip_hash >> 4) % len(self._fallback_asns)]
        
        return country, asn
