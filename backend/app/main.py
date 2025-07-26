from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.market_data import router as market_data_router

app = FastAPI(
    title="PAViewer API",
    description="Price Action Viewer - Trading Analysis API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(market_data_router)

@app.get("/")
async def root():
    return {"message": "PAViewer API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}