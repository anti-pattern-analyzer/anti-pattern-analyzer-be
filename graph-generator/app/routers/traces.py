from fastapi import APIRouter

from app.services import fetch_services, fetch_and_store_traces_for_all_services

router = APIRouter()


@router.get("/services")
async def get_all_services():
    services = fetch_services()
    return {"status": "success", "data": services}


@router.get("")
async def get_all_traces():
    services = fetch_and_store_traces_for_all_services()
    return {"status": "success", "data": services}
