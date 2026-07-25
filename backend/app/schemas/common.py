"""
MuleTrace AI — Common Schemas.

Defines reusable API response envelopes, pagination models, and standard error structures.
Uses Pydantic v2 standards.
"""

from __future__ import annotations


from typing import Optional, Any, Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    """Standardized API response envelope for all endpoints."""

    model_config = ConfigDict(from_attributes=True)

    success: bool = Field(default=True, description="Indicates if request succeeded")
    message: str = Field(default="Operation completed successfully", description="Status message")
    data: Optional[T] = Field(default=None, description="Response payload")


class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class PaginationMeta(BaseModel):
    """Pagination metadata included in paginated responses."""

    total_items: int = Field(..., description="Total count of matching items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="True if next page exists")
    has_prev: bool = Field(..., description="True if previous page exists")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard envelope for paginated list responses."""

    success: bool = True
    message: str = "Data retrieved successfully"
    data: list[T]
    pagination: PaginationMeta


class ErrorDetail(BaseModel):
    """Detailed error item in validation failure responses."""

    loc: list[str] = Field(default_factory=list, description="Field location path")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error code / type")


class ErrorResponse(BaseModel):
    """Standard error response payload."""

    success: bool = False
    message: str = Field(..., description="High-level error summary")
    error_code: str = Field(default="INTERNAL_ERROR", description="Machine-readable error code")
    details: Optional[list[ErrorDetail]] = Field(default=None, description="Field-level errors if any")
