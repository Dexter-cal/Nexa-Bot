import time
import json
import logging
from typing import List, Dict, Any, Optional
import datetime

logger = logging.getLogger(__name__)

class VectorMemory:
    """
    Searchable long-term memory layer
    """
    def __init__(self):
        self.store: List[Dict[str, Any]] = []

    async def add(self, text: str, metadata: Dict[str, Any] = None):
        """
        Add an entry to long-term memory
        """
        entry = {
            "id": len(self.store),
            "text": text,
            "metadata": metadata or {},
            "timestamp": datetime.datetime.now().isoformat(),
            # In a real system, we would store embeddings here
            "embedding": None
        }
        self.store.append(entry)
        logger.debug(f"Memory added: {text[:50]}...")

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Simulated vector search using simple keyword matching
        """
        query_words = set(query.lower().split())
        results = []

        for entry in self.store:
            entry_words = set(entry["text"].lower().split())
            intersection = query_words.intersection(entry_words)
            if intersection:
                results.append((len(intersection), entry))

        # Sort by match count
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:limit]]

class TimeCapsule:
    """
    Generates periodic summaries of activities
    """
    def __init__(self, memory: VectorMemory):
        self.memory = memory

    async def generate_weekly_summary(self) -> str:
        # Fetch last week's memories
        now = datetime.datetime.now()
        last_week = now - datetime.timedelta(days=7)

        relevant_memories = [
            m for m in self.memory.store
            if datetime.datetime.fromisoformat(m["timestamp"]) > last_week
        ]

        if not relevant_memories:
            return "No activities recorded this week."

        summary = f"Weekly Activity Summary ({last_week.date()} to {now.date()}):\n"
        for m in relevant_memories:
            summary += f"- [{m['timestamp']}] {m['text'][:100]}\n"

        return summary
