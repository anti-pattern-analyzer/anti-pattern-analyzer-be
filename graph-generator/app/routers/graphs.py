from fastapi import APIRouter
from app.services.graph_processor import generate_dependency_graph

router = APIRouter()


@router.post("/")
async def create_dependency_graph():
    return {"status": "success", "graph": "generate graph"}
