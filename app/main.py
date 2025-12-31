from fastapi import FastAPI, Request

from app.controller.api_v1 import api_router
from app.controller.health import router as health_router

from fastapi.responses import JSONResponse

from app.exceptions.api_exceptions import APIError
app = FastAPI(title="Movie Rating System")

@app.exception_handler(APIError)
def api_error_handler(request: Request, exc: APIError):
    return JSONResponse(
        status_code=exc.code,
        content={
            "status": "failure",
            "error": {"code": exc.code, "message": exc.message},
        },
    )

# non-versioned routes (like health)
app.include_router(health_router)

# versioned API routes: /api/v1/...
app.include_router(api_router)
