from fastapi import FastAPI
from app.routers import traces_router, graphs_router

app = FastAPI(title="Graph Generator")

# Include API routers
app.include_router(traces_router, prefix="/api/traces", tags=["Traces"])
app.include_router(graphs_router, prefix="/api/graphs", tags=["Graphs"])


@app.on_event("startup")
async def startup():
    print("Starting up: Initializing database connection...")


@app.on_event("shutdown")
async def shutdown():
    print("Shutting down: Closing database connection...")


@app.get("/")
async def root():
    return {"message": "Graph Generator API is running"}
