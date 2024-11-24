from fastapi import FastAPI
from app.routers import traces_router, graphs_router

app = FastAPI(title="Graph Generator")

# Include API routers
app.include_router(traces_router, prefix="/api/traces", tags=["Traces"])
app.include_router(graphs_router, prefix="/api/graphs", tags=["Graphs"])


@app.get("/")
async def root():
    return {"message": "Graph Generator API is runningggg"}
