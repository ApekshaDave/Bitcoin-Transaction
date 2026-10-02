from typing import Dict, Any, List

class MixingPatternDetector:
    """
    Mixing-Like Structural Pattern Classifier.
    Analyzes transaction input/output symmetry, output value entropy, 
    and multi-participant equalized value distribution (e.g., CoinJoin structures).
    """
    def __init__(self, entropy_threshold: float = 1.5):
        self.entropy_threshold = entropy_threshold

    def analyze_mixing_patterns(self, transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Scores mixing-like structural patterns per TXID.
        Returns Dict[txid, {"mixing_score": float, "explanation": str}]
        """
        results = {}

        for tx in transactions:
            txid = tx["txid"]
            in_cnt = tx.get("input_count", 0)
            out_cnt = tx.get("output_count", 0)
            entropy = tx.get("output_entropy", 0.0)
            outputs = tx.get("outputs", [])

            # Check output amount equality
            amounts = [o.get("amount", 0) for o in outputs if o.get("amount", 0) > 0]
            if len(amounts) > 1:
                amt_std = float(pd.Series(amounts).std()) if len(amounts) > 1 else 0.0
                amt_mean = float(pd.Series(amounts).mean()) if len(amounts) > 1 else 1.0
                cv = amt_std / max(1.0, amt_mean)  # Coefficient of variation
            else:
                cv = 1.0

            # Structural mixing criteria: multi-input, multi-output, symmetric, high entropy, equalized amounts
            is_symmetric = (in_cnt >= 3 and in_cnt == out_cnt)
            is_high_entropy = (entropy >= self.entropy_threshold)
            is_equal_outputs = (cv < 0.05 and len(amounts) >= 3)

            if is_symmetric and is_equal_outputs and is_high_entropy:
                mixing_score = 0.95
                explanation = f"Equalized CoinJoin-like structure detected ({in_cnt}-in {out_cnt}-out, entropy={entropy:.2f}, cv={cv:.4f})."
            elif (in_cnt >= 3 and out_cnt >= 3) and is_equal_outputs:
                mixing_score = 0.80
                explanation = f"Multi-party output equalization detected ({in_cnt}-in {out_cnt}-out, equal amounts)."
            elif is_symmetric:
                mixing_score = 0.50
                explanation = f"Symmetric input-output structure ({in_cnt}-in {out_cnt}-out)."
            else:
                mixing_score = 0.0
                explanation = "Standard transaction layout."

            results[txid] = {
                "mixing_score": round(mixing_score, 4),
                "entropy": entropy,
                "explanation": explanation
            }

        return results

import pandas as pd
