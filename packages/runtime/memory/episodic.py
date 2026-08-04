"""
Episodic Memory — Historical Task Traces & Outcome Logs
"""
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("atlas.memory.episodic")


@dataclass
class Episode:
    id: str
    goal: str
    status: str
    steps_executed: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    outcome_summary: str = ""
    timestamp: float = field(default_factory=time.time)


class EpisodicMemory:
    def __init__(self):
        self._episodes: Dict[str, Episode] = {}

    def record_episode(self, episode: Episode):
        self._episodes[episode.id] = episode
        logger.info(f"Recorded episodic memory for task: {episode.id}")

    def get_episode(self, episode_id: str) -> Optional[Episode]:
        return self._episodes.get(episode_id)

    def search_episodes(self, query: str, limit: int = 5) -> List[Episode]:
        q_lower = query.lower()
        matched = [
            ep for ep in self._episodes.values()
            if q_lower in ep.goal.lower() or q_lower in ep.outcome_summary.lower()
        ]
        return matched[:limit]
