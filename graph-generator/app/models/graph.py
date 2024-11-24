from pydantic import BaseModel
from typing import List, Dict


class GraphNode(BaseModel):
    id: str
    label: str


class GraphEdge(BaseModel):
    source: str
    target: str
    weight: float


class DependencyGraph(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
