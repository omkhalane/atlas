"""
Tool Adapter — Schema Converter for Providers
"""
from typing import List, Dict, Any
from runtime.llm.contracts import ToolDefinition


class ToolAdapter:
    @staticmethod
    def to_openai(tools: List[ToolDefinition]) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters
                }
            }
            for t in tools
        ]

    @staticmethod
    def to_anthropic(tools: List[ToolDefinition]) -> List[Dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.parameters
            }
            for t in tools
        ]

    @staticmethod
    def to_gemini(tools: List[ToolDefinition]) -> List[Dict[str, Any]]:
        declarations = []
        for t in tools:
            declarations.append({
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters
            })
        return [{"function_declarations": declarations}]
