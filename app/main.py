from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import traceback
import logging

from app.controller.api_v1 import api_router
from app.controller.health import router as health_router

from app.exceptions.api_exceptions import APIError

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Movie Rating System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(APIError)
def api_error_handler(request: Request, exc: APIError):
    return JSONResponse(
        status_code=exc.code,
        content={
            "status": "failure",
            "error": {"code": exc.code, "message": exc.message},
        },
    )


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with detailed logging."""
    error_msg = str(exc)
    logger.error(
        f"Unhandled exception in {request.url.path}: {error_msg}\n"
        f"Method: {request.method}\n"
        f"Headers: {dict(request.headers)}\n"
        f"Query params: {dict(request.query_params)}",
        exc_info=True
    )
    import sys
    traceback.print_exc(file=sys.stderr)
    return JSONResponse(
        status_code=500,
        content={
            "status": "failure",
            "error": {"code": 500, "message": error_msg},
        },
    )

# non-versioned routes (like health)
app.include_router(health_router)

# versioned API routes: /api/v1/...
app.include_router(api_router)
