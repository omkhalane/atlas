"""
Knowledge Memory — Entity-Relationship Graph Memory
"""
from typing import Dict, List, Any


class KnowledgeMemory:
    def __init__(self):
        self._entities: Dict[str, Dict[str, Any]] = {}
        self._relations: List[Dict[str, str]] = []

    def add_entity(self, entity_id: str, attributes: Dict[str, Any]):
        self._entities[entity_id] = attributes

    def add_relation(self, source: str, relation: str, target: str):
        self._relations.append({"source": source, "relation": relation, "target": target})

    def get_relations_for(self, entity_id: str) -> List[Dict[str, str]]:
        return [r for r in self._relations if r["source"] == entity_id or r["target"] == entity_id]
