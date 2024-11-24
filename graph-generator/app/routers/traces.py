from fastapi import APIRouter
from app.services.data_collector import fetch_and_store_traces

router = APIRouter()

@router.post("/{service_name}")
async def collect_traces(service_name: str):
    traces = fetch_and_store_traces(service_name)
    return {"status": "success", "traces_collected": len(traces)}
