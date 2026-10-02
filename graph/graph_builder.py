import networkx as nx
from typing import List, Dict, Any, Optional

class HeterogeneousGraphBuilder:
    """
    Builds and manages the Heterogeneous Network Graph linking:
    Nodes: IP, Transaction (TXID), Address
    Edges: 
      - (IP) -[OBSERVED_IN]-> (Transaction)
      - (Address) -[INPUT_TO]-> (Transaction)
      - (Transaction) -[OUTPUTS_TO]-> (Address)
      - (Transaction) -[SPENDS]-> (Transaction)
    """
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph(
        self, 
        transactions: List[Dict[str, Any]], 
        network_observations: List[Dict[str, Any]],
        entity_mappings: Optional[Dict[str, str]] = None
    ) -> nx.DiGraph:
        """
        Populates NetworkX directed graph from preprocessed data.
        entity_mappings: Optional Dict[address, entity_id] from clustering engine.
        """
        entity_map = entity_mappings or {}

        # 1. Add Transaction nodes
        for tx in transactions:
            txid = tx["txid"]
            self.graph.add_node(
                f"tx:{txid}",
                node_type="Transaction",
                label=f"TX: {txid[:8]}...",
                txid=txid,
                timestamp=tx.get("timestamp"),
                total_amount=tx.get("total_input_amount", 0),
                fee=tx.get("fee", 0),
                input_count=tx.get("input_count", 0),
                output_count=tx.get("output_count", 0)
            )

            # Process Inputs & SPENDS edges
            for inp in tx.get("inputs", []):
                addr = inp.get("address")
                amount = inp.get("amount", 0)
                vout = inp.get("vout_index", 0)
                prev_txid = inp.get("prev_txid")

                if addr:
                    addr_node_id = f"addr:{addr}"
                    if not self.graph.has_node(addr_node_id):
                        self.graph.add_node(
                            addr_node_id,
                            node_type="Address",
                            label=f"Addr: {addr[:8]}...",
                            address=addr,
                            entity_id=entity_map.get(addr, "unclustered")
                        )
                    # Edge: Address -> Transaction
                    self.graph.add_edge(
                        addr_node_id,
                        f"tx:{txid}",
                        edge_type="INPUT",
                        amount=amount,
                        vout_index=vout
                    )

                # Edge: Transaction A -> Transaction B (SPENDS previous output)
                if prev_txid and self.graph.has_node(f"tx:{prev_txid}"):
                    self.graph.add_edge(
                        f"tx:{prev_txid}",
                        f"tx:{txid}",
                        edge_type="SPENDS",
                        prev_vout_index=vout,
                        amount=amount
                    )

            # Process Outputs
            for out in tx.get("outputs", []):
                addr = out.get("address")
                amount = out.get("amount", 0)
                vout = out.get("vout_index", 0)
                script_type = out.get("script_type", "P2WPKH")

                if addr:
                    addr_node_id = f"addr:{addr}"
                    if not self.graph.has_node(addr_node_id):
                        self.graph.add_node(
                            addr_node_id,
                            node_type="Address",
                            label=f"Addr: {addr[:8]}...",
                            address=addr,
                            entity_id=entity_map.get(addr, "unclustered")
                        )
                    # Edge: Transaction -> Address
                    self.graph.add_edge(
                        f"tx:{txid}",
                        addr_node_id,
                        edge_type="OUTPUT",
                        amount=amount,
                        vout_index=vout,
                        script_type=script_type
                    )

        # 2. Add Network IP nodes & OBSERVED edges
        for obs in network_observations:
            txid = obs["txid"]
            ip = obs["src_ip"]
            ip_node_id = f"ip:{ip}"

            if not self.graph.has_node(ip_node_id):
                self.graph.add_node(
                    ip_node_id,
                    node_type="IP",
                    label=f"IP: {ip}",
                    address=ip,
                    country=obs.get("geo_country", "UNKNOWN"),
                    asn=obs.get("asn", "UNKNOWN")
                )

            if self.graph.has_node(f"tx:{txid}"):
                self.graph.add_edge(
                    ip_node_id,
                    f"tx:{txid}",
                    edge_type="OBSERVED",
                    timestamp=obs.get("timestamp"),
                    src_port=obs.get("src_port", 8333),
                    dst_port=obs.get("dst_port", 8333),
                    time_delta=obs.get("time_delta", 0.0)
                )

        # 3. Add Entity nodes & ASSOCIATED_WITH edges for all addresses
        if not entity_map:
            entity_map = {}

        for n, data in list(self.graph.nodes(data=True)):
            if data.get("node_type") == "Address":
                addr = data.get("address") or n.replace("addr:", "")
                ent_id = entity_map.get(addr)
                if not ent_id:
                    ent_id = f"entity_cand_{addr[:6]}"
                ent_node_id = f"entity:{ent_id}"
                if not self.graph.has_node(ent_node_id):
                    self.graph.add_node(
                        ent_node_id,
                        node_type="Entity",
                        label=f"Entity: {ent_id}",
                        entity_id=ent_id
                    )
                if not self.graph.has_edge(n, ent_node_id):
                    self.graph.add_edge(
                        n,
                        ent_node_id,
                        edge_type="ASSOCIATED_WITH"
                    )

        return self.graph

    def export_to_cytoscape_json(self, center_node_id: str = None, depth: int = 2, max_nodes: int = 50, max_edges: int = 100) -> Dict[str, Any]:
        """
        Exports a strictly bounded neighborhood subgraph into Cytoscape.js format JSON payload 
        to ensure fast network transfer and prevent browser freezes.
        """
        MAX_SAFETY_NODES = 200
        MAX_SAFETY_EDGES = 500

        effective_max_nodes = min(max_nodes, MAX_SAFETY_NODES)
        effective_max_edges = min(max_edges, MAX_SAFETY_EDGES)

        if not self.graph.nodes():
            return {
                "node_count": 0,
                "edge_count": 0,
                "depth": depth,
                "center": center_node_id,
                "truncated": False,
                "elements": []
            }

        # Resolve center node (support case-insensitive txid matching)
        actual_center = None
        if center_node_id:
            if self.graph.has_node(center_node_id):
                actual_center = center_node_id
            else:
                c_lower = center_node_id.lower()
                for n in self.graph.nodes():
                    if n.lower() == c_lower or n.lower() == f"tx:{c_lower}" or n.lower() == f"addr:{c_lower}" or n.lower() == f"ip:{c_lower}":
                        actual_center = n
                        break

        # If center node is specified/resolved, perform BFS neighborhood traversal
        if actual_center:
            sub_nodes = set([actual_center])
            current_layer = set([actual_center])
            for _ in range(depth):
                next_layer = set()
                for n in current_layer:
                    for neighbor in list(self.graph.successors(n)) + list(self.graph.predecessors(n)):
                        if len(sub_nodes) < effective_max_nodes:
                            sub_nodes.add(neighbor)
                            next_layer.add(neighbor)
                        else:
                            break
                    if len(sub_nodes) >= effective_max_nodes:
                        break
                current_layer = next_layer
                if len(sub_nodes) >= effective_max_nodes:
                    break
            target_graph = self.graph.subgraph(sub_nodes)
        else:
            # Pick transaction nodes first up to effective_max_nodes
            tx_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("node_type") == "Transaction"]
            if not tx_nodes:
                tx_nodes = list(self.graph.nodes())
            
            golden_txs = [n for n in tx_nodes if "golden" in n.lower()]
            other_txs = [n for n in tx_nodes if "golden" not in n.lower()]
            ordered_txs = golden_txs + other_txs
            
            selected_nodes = set(ordered_txs[:min(10, len(ordered_txs))])
            # Add 2-hop neighbors for selected transaction nodes up to max_nodes
            hop1 = set()
            for n in list(selected_nodes):
                for neighbor in list(self.graph.successors(n)) + list(self.graph.predecessors(n)):
                    hop1.add(neighbor)
            selected_nodes.update(hop1)
            
            hop2 = set()
            for n in list(hop1):
                for neighbor in list(self.graph.successors(n)) + list(self.graph.predecessors(n)):
                    hop2.add(neighbor)
            selected_nodes.update(hop2)
            
            if len(selected_nodes) > effective_max_nodes:
                golden_in_sel = [n for n in selected_nodes if "golden" in n.lower()]
                other_in_sel = [n for n in selected_nodes if "golden" not in n.lower()]
                selected_nodes = set(golden_in_sel + other_in_sel[:max(0, effective_max_nodes - len(golden_in_sel))])

            target_graph = self.graph.subgraph(selected_nodes)

        elements = []
        node_count = target_graph.number_of_nodes()
        edge_count = 0
        truncated = node_count < self.graph.number_of_nodes()

        # Nodes payload (compact metadata)
        for n, data in target_graph.nodes(data=True):
            elements.append({
                "data": {
                    "id": n,
                    "label": data.get("label", n),
                    "node_type": data.get("node_type", "Unknown"),
                    "type": data.get("node_type", "Unknown"),
                    "classLabel": data.get("classLabel"),
                    "risk_score": data.get("risk_score", 0),
                    "address": data.get("address"),
                    "country": data.get("country"),
                    "asn": data.get("asn")
                }
            })

        # Edges payload (capped at effective_max_edges)
        for u, v, data in target_graph.edges(data=True):
            if edge_count >= effective_max_edges:
                truncated = True
                break
            edge_id = f"e_{u}_{v}_{data.get('edge_type', 'LINK')}"
            elements.append({
                "data": {
                    "id": edge_id,
                    "source": u,
                    "target": v,
                    "label": data.get("edge_type", "LINK"),
                    "edge_type": data.get("edge_type", "LINK")
                }
            })
            edge_count += 1

        return {
            "node_count": len(elements) - edge_count,
            "edge_count": edge_count,
            "depth": depth,
            "center": actual_center or center_node_id,
            "truncated": truncated,
            "elements": elements
        }
