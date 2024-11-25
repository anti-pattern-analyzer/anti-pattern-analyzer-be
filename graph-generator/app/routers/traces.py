from fastapi import APIRouter, HTTPException
from app.services.graph_processor import get_graph_data_as_json

router = APIRouter()


@router.post("/create")
async def create_dependency_graph():
    try:
        update_dependency_graph()
        return {"status": "success", "message": "Dependency graph updated successfully."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to update graph: {str(e)}"}


@router.get("/")
async def retrieve_dependency_graph():
    try:
        graph_data = get_graph_data_as_json()
        return {"status": "success", "graph": graph_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve graph: {str(e)}")
