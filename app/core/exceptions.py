from datetime import datetime, timezone
from typing import Any
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
    details: Any = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AppException(Exception):
    def __init__(self, status_code: int, detail: str, error_code: str):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        super().__init__(self.detail)


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail, error_code="NOT_FOUND")


class DuplicateException(AppException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=409, detail=detail, error_code="DUPLICATE_RESOURCE")


class GooglePlacesAPIError(AppException):
    def __init__(self, detail: str = "Google Places API Error"):
        super().__init__(status_code=502, detail=detail, error_code="GOOGLE_PLACES_ERROR")


class GoogleVisionAPIError(AppException):
    def __init__(self, detail: str = "Google Vision API Error"):
        super().__init__(status_code=502, detail=detail, error_code="GOOGLE_VISION_ERROR")


class LLMServiceError(AppException):
    def __init__(self, detail: str = "LLM Service Error"):
        super().__init__(status_code=502, detail=detail, error_code="LLM_SERVICE_ERROR")


class DatabaseError(AppException):
    def __init__(self, detail: str = "Database Error"):
        super().__init__(status_code=500, detail=detail, error_code="DATABASE_ERROR")


class ValidationError(AppException):
    def __init__(self, detail: str = "Validation Error"):
        super().__init__(status_code=422, detail=detail, error_code="VALIDATION_ERROR")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        error = ErrorResponse(error_code=exc.error_code, message=exc.detail)
        return JSONResponse(status_code=exc.status_code, content=error.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        error = ErrorResponse(
            error_code="UNPROCESSABLE_ENTITY",
            message="Request validation failed",
            details=exc.errors()
        )
        return JSONResponse(status_code=422, content=error.model_dump())

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        error = ErrorResponse(error_code="DATABASE_ERROR", message="An unexpected database error occurred.")
        return JSONResponse(status_code=500, content=error.model_dump())

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        error = ErrorResponse(error_code="INTERNAL_SERVER_ERROR", message="An unexpected error occurred.")
        return JSONResponse(status_code=500, content=error.model_dump())
