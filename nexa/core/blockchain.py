import hashlib
import json
import time
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class Block:
    def __init__(self, index: int, timestamp: float, data: Any, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class AuditBlockchain:
    """
    Lightweight, local blockchain for immutable audit logs.
    """
    def __init__(self):
        self.chain: List[Block] = [self.create_genesis_block()]
        logger.info("Audit Blockchain initialized.")

    def create_genesis_block(self) -> Block:
        return Block(0, time.time(), "Genesis Block - Nexa Bot Audit Trail", "0")

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_block(self, data: Any):
        previous_block = self.get_latest_block()
        new_block = Block(
            index=previous_block.index + 1,
            timestamp=time.time(),
            data=data,
            previous_hash=previous_block.hash
        )
        self.chain.append(new_block)
        logger.debug(f"Block #{new_block.index} added to audit chain.")

        # In a real app, persist this to disk (encrypted)
        self._persist_chain()

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def _persist_chain(self):
        if os.getenv("NEXA_ETHEREAL_MODE") == "true":
            return
        # Placeholder for encrypted persistence
        pass

    def get_history(self, count: int = 50) -> List[Dict[str, Any]]:
        return [
            {
                "index": b.index,
                "timestamp": b.timestamp,
                "data": b.data,
                "hash": b.hash
            }
            for b in self.chain[-count:]
        ]
