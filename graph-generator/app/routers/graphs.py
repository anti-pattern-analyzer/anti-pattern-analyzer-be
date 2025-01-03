from fastapi import APIRouter

from app.services import get_all_traces_from_mongo
from app.services.graph_processor import (
    generate_weighted_graph_from_traces,
    update_graph_in_neo4j,
    get_graph_data_as_json, get_anti_patterns_using_graph_data, analyze_endpoint_usage
)
from app.services.graph_updater import fetch_new_traces_since_last_sync, update_last_sync_date

router = APIRouter()


@router.post("/create")
async def create_dependency_graph():
    """
    Endpoint to create or update the dependency graph.
    """
    try:
        new_traces = fetch_new_traces_since_last_sync()
        if not new_traces:
            return {"status": "success", "message": "No new traces to process."}

        graph = generate_weighted_graph_from_traces(new_traces)
        update_graph_in_neo4j(graph)

        # Ensure `startTime` is accessed safely
        latest_sync_date = max(
            span["startTime"] if isinstance(span["startTime"], int) else int(span["startTime"]["$numberLong"])
            for trace in new_traces for span in trace["spans"]
        )
        update_last_sync_date(latest_sync_date)

        return {"status": "success", "message": "Dependency graph updated successfully."}
    except Exception as e:
        return {"status": "error", "message": f"Failed to update graph: {str(e)}"}


@router.get("/")
async def fetch_dependency_graph():
    """
    Endpoint to fetch the dependency graph as JSON data.
    """
    try:
        graph_data = get_graph_data_as_json()
        return {"status": "success", "graph": graph_data}
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch graph: {str(e)}"}

@router.get("/patterns")
async def fetch_dependency_graph_patterns():
    try:
        graph_data = get_graph_data_as_json()
        patterns = get_anti_patterns_using_graph_data(graph_data)
        return {"status": "success", "patterns": patterns}
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch graph: {str(e)}"}


@router.get("/endpoint/usage")
async def fetch_dependency_graph_patterns():
    try:
        traces = get_all_traces_from_mongo()
        endpoints = analyze_endpoint_usage(traces)
        return {"status": "success", "endpoints": endpoints}
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch graph: {str(e)}"}
