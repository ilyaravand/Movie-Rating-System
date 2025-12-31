from fastapi import FastAPI

from app.controller.api_v1 import api_router
from app.controller.health import router as health_router

app = FastAPI(title="Movie Rating System")

# non-versioned routes (like health)
app.include_router(health_router)

# versioned API routes: /api/v1/...
app.include_router(api_router)
