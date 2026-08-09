from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

class CapabilitySchema(BaseModel):
    id: str = Field(..., description="Unique capability ID, e.g. github.repository.read")
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: List[str] = Field(default_factory=list, description="Permissions required to execute this capability")

class ToolSchema(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any] = Field(default_factory=dict, alias="schema")

class PermissionSchema(BaseModel):
    id: str
    description: str
    dangerous: bool = False

class AuthSchema(BaseModel):
    type: Literal["oauth", "api_key", "token", "env", "local", "custom", "none"] = "none"
    config: Dict[str, Any] = Field(default_factory=dict)

class ManifestSchema(BaseModel):
    id: str
    name: str
    version: str
    publisher: str
    description: str
    icon: Optional[str] = None
    type: Literal["plugin", "mcp", "ai_provider"]
    capabilities: List[CapabilitySchema] = Field(default_factory=list)
    permissions: List[PermissionSchema] = Field(default_factory=list)
    authentication: AuthSchema = Field(default_factory=AuthSchema)
    tools: List[ToolSchema] = Field(default_factory=list)
    configuration: Dict[str, Any] = Field(default_factory=dict)
    runtime: Dict[str, Any] = Field(default_factory=dict)
    health_check: bool = True
