from fastapi import APIRouter
from typing import Optional
from fastapi import Query
from app.services.graph_processor import (get_graph_data_as_json)
from app.services.coupling_metrics_calculator import (
    calculate_ais, calculate_all_ais)

router = APIRouter()

@router.get("/absolute-importance-of")
async def get_absolute_importance_of_a_service(service: Optional[str] = Query(None)):
    """
    Endpoint to process the absolute importance of a service.
    """
    try:
        graph_data = get_graph_data_as_json()
        if service is not None:
            ais = calculate_ais(service, graph_data)
            return {"status": "success", "data": ais}
        else:
            all_ais = calculate_all_ais(graph_data)
            return {"status": "success", "data": all_ais}
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch graph: {str(e)}"}


@router.get("/")
async def coupling_health():
    """
    Endpoint to fetch the dependency graph as JSON data.
    """
    try:
        graph_data = get_graph_data_as_json()
        return {"status": "success", "graph": graph_data}
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch graph: {str(e)}"}