from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.database.connection import init_db
from backend.api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Canonical Error Response Helper
def build_error_response(code: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    code_map = {
        status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
        status.HTTP_404_NOT_FOUND: "RESOURCE_NOT_FOUND",
        getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422): "SCHEMA_MISMATCH",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "INTERNAL_ERROR",
    }
    code = code_map.get(exc.status_code, "ERROR")
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return build_error_response(code=code, message=message, status_code=exc.status_code)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    messages = []
    for err in errors:
        loc = " -> ".join(str(p) for p in err.get("loc", []) if p != "body")
        msg = err.get("msg", "Invalid field")
        messages.append(f"{loc}: {msg}" if loc else msg)
    summary_msg = "; ".join(messages) if messages else "Validation failed for request payload."
    return build_error_response(
        code="VALIDATION_ERROR",
        message=summary_msg,
        status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422),
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return build_error_response(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected server error occurred.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

# Include canonical versioned API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
