import hashlib
import random
import time
from typing import List, Dict, Any, Tuple

class BitcoinDataGenerator:
    """
    Synthetic Bitcoin Transaction Data Generator.
    Generates realistic Bitcoin transactions with inputs, outputs, fee estimation, 
    script types, and prev_txid output spending chains.
    """
    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.address_pool: List[str] = [self._generate_address() for _ in range(100)]
        self.unspent_outputs: List[Dict[str, Any]] = []  # Pool of available UTXOs for spending chains
        self.tx_counter = 0

    def _generate_address(self) -> str:
        """Generates a synthetic Bitcoin address (P2PKH, P2SH, or Bech32 format)."""
        prefix = random.choice(["1", "3", "bc1q"])
        chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        if prefix == "bc1q":
            chars = "023456789acdefghjklmnpqrstuvwxyz"
            suffix = "".join(random.choices(chars, k=38))
        else:
            suffix = "".join(random.choices(chars, k=33))
        return f"{prefix}{suffix}"

    def _generate_txid(self, index: int, timestamp: float) -> str:
        raw = f"tx_{index}_{timestamp}_{random.random()}"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    def create_genesis_utxos(self, count: int = 50) -> None:
        """Seeds initial UTXOs to bootstrap transaction chains."""
        base_time = time.time() - 86400
        for i in range(count):
            txid = self._generate_txid(i, base_time)
            addr = random.choice(self.address_pool)
            amount = random.randint(500000, 50000000)  # 0.005 to 0.5 BTC in Sats
            self.unspent_outputs.append({
                "txid": txid,
                "vout_index": 0,
                "address": addr,
                "amount": amount
            })

    def generate_single_transaction(
        self, 
        timestamp: str,
        input_count: int = 1,
        output_count: int = 2,
        forced_inputs: List[Dict[str, Any]] = None,
        forced_outputs: List[Tuple[str, int, bool]] = None,
        block_height: int = 800000
    ) -> Dict[str, Any]:
        """
        Generates a single synthetic Bitcoin transaction.
        
        Args:
            timestamp: ISO8601 string or timestamp
            input_count: Number of inputs to select from available UTXO pool
            output_count: Number of outputs to create
            forced_inputs: Optional specific UTXOs to spend (for peeling chains / mixing)
            forced_outputs: Optional specific (address, amount, is_change) tuples
            block_height: Synthetic block height
        """
        self.tx_counter += 1
        txid = self._generate_txid(self.tx_counter, time.time())

        # Select inputs
        selected_inputs = []
        if forced_inputs:
            selected_inputs = forced_inputs
        else:
            if len(self.unspent_outputs) < input_count:
                # Top up UTXOs if pool is low
                self.create_genesis_utxos(count=10)
            
            # Pop UTXOs from available pool
            for _ in range(min(input_count, len(self.unspent_outputs))):
                utxo = self.unspent_outputs.pop(random.randint(0, len(self.unspent_outputs) - 1))
                selected_inputs.append(utxo)

        total_input_amount = sum(inp["amount"] for inp in selected_inputs)
        fee = max(1000, int(total_input_amount * random.uniform(0.001, 0.01)))
        available_output_amount = total_input_amount - fee

        # Construct inputs schema
        inputs_data = []
        for idx, inp in enumerate(selected_inputs):
            inputs_data.append({
                "id": len(inputs_data) + 1,
                "txid": txid,
                "prev_txid": inp["txid"],
                "prev_vout_index": inp["vout_index"],
                "address": inp["address"],
                "amount": inp["amount"]
            })

        # Construct outputs schema
        outputs_data = []
        if forced_outputs:
            for vout_idx, (addr, amt, is_change) in enumerate(forced_outputs):
                script_type = "P2WPKH" if addr.startswith("bc1") else ("P2SH" if addr.startswith("3") else "P2PKH")
                outputs_data.append({
                    "id": vout_idx + 1,
                    "txid": txid,
                    "address": addr,
                    "amount": amt,
                    "script_type": script_type,
                    "is_change_ground_truth": 1 if is_change else 0
                })
                # Add to unspent pool for future spending chains
                self.unspent_outputs.append({
                    "txid": txid,
                    "vout_index": vout_idx,
                    "address": addr,
                    "amount": amt
                })
        else:
            # Standard output generation: split available_output_amount across outputs
            if output_count == 1:
                amounts = [available_output_amount]
                is_change_flags = [False]
            else:
                # First output is payment, second is change
                pay_amt = int(available_output_amount * random.uniform(0.3, 0.7))
                change_amt = available_output_amount - pay_amt
                amounts = [pay_amt, change_amt]
                is_change_flags = [False, True]

            for vout_idx in range(len(amounts)):
                addr = random.choice(self.address_pool)
                is_change = is_change_flags[vout_idx] if vout_idx < len(is_change_flags) else False
                script_type = "P2WPKH" if addr.startswith("bc1") else ("P2SH" if addr.startswith("3") else "P2PKH")
                outputs_data.append({
                    "id": vout_idx + 1,
                    "txid": txid,
                    "address": addr,
                    "amount": amounts[vout_idx],
                    "script_type": script_type,
                    "is_change_ground_truth": 1 if is_change else 0
                })
                # Add output to available UTXO pool
                self.unspent_outputs.append({
                    "txid": txid,
                    "vout_index": vout_idx,
                    "address": addr,
                    "amount": amounts[vout_idx]
                })

        total_output_amount = sum(out["amount"] for out in outputs_data)
        size_bytes = 148 * len(inputs_data) + 34 * len(outputs_data) + 10
        weight_units = size_bytes * 4

        tx_record = {
            "txid": txid,
            "timestamp": timestamp,
            "fee": fee,
            "size": size_bytes,
            "weight": weight_units,
            "block_height": block_height,
            "input_count": len(inputs_data),
            "output_count": len(outputs_data),
            "total_input_amount": total_input_amount,
            "total_output_amount": total_output_amount,
            "inputs": inputs_data,
            "outputs": outputs_data
        }
        return tx_record
