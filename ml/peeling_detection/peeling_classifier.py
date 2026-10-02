import networkx as nx
from typing import Dict, Any, List

class PeelingChainDetector:
    """
    Peeling-Chain Structural Pattern Detector.
    Analyzes transaction sequences for characteristic peeling behavior:
    1 input -> 1 dominant continuation output + 1 small payment output, 
    repeated across sequential transactions along SPENDS graph edges.
    """
    def __init__(self, min_chain_length: int = 3):
        self.min_chain_length = min_chain_length

    def analyze_peeling_chains(
        self, 
        graph: nx.DiGraph, 
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Analyzes graph and transaction data to score peeling-chain behavior per TXID.
        Returns Dict[txid, {"peeling_score": float, "chain_length": int, "explanation": str}]
        """
        tx_dict = {tx["txid"]: tx for tx in transactions}
        results = {}

        for tx in transactions:
            txid = tx["txid"]
            outputs = tx.get("outputs", [])
            in_cnt = tx.get("input_count", 0)
            out_cnt = tx.get("output_count", 0)

            # Peeling chain links typically have 1-2 inputs and 2 outputs (continuation + payment)
            if out_cnt != 2 or in_cnt > 2:
                results[txid] = {
                    "peeling_score": 0.0,
                    "chain_length": 0,
                    "explanation": "Standard output structure"
                }
                continue

            # Check output amount disparity (1 dominant continuation, 1 small payment)
            amounts = sorted([o.get("amount", 0) for o in outputs], reverse=True)
            if len(amounts) == 2 and amounts[0] > 0:
                cont_ratio = amounts[0] / (amounts[0] + amounts[1])
                pay_ratio = amounts[1] / (amounts[0] + amounts[1])
            else:
                cont_ratio, pay_ratio = 0.5, 0.5

            # Trace forward SPENDS graph chain length
            node_id = f"tx:{txid}"
            chain_len = 1
            if graph.has_node(node_id):
                curr = node_id
                while True:
                    spends_succs = [
                        v for u, v, d in graph.out_edges(curr, data=True) 
                        if d.get("edge_type") == "SPENDS"
                    ]
                    if spends_succs:
                        chain_len += 1
                        curr = spends_succs[0]
                    else:
                        break

            # Calculate peeling score
            if cont_ratio >= 0.85 and chain_len >= self.min_chain_length:
                peeling_score = min(1.0, 0.6 + 0.1 * chain_len)
                explanation = f"Repeated sequential transactions with dominant continuation output ({cont_ratio*100:.1f}%) across chain length {chain_len}."
            elif cont_ratio >= 0.85:
                peeling_score = round(0.4 * cont_ratio, 4)
                explanation = f"Single peeling link structure detected (continuation output {cont_ratio*100:.1f}%)."
            else:
                peeling_score = 0.0
                explanation = "Balanced output amounts (no peeling disparity)."

            results[txid] = {
                "peeling_score": round(peeling_score, 4),
                "chain_length": chain_len,
                "explanation": explanation
            }

        return results
