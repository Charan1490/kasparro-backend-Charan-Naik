"""Pydantic schemas for API requests and responses."""
from datetime import datetime
from typing import List, Optional, Any, Dict

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Pagination parameters."""
    
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=100, description="Items per page")


class FilterParams(BaseModel):
    """Filter parameters."""
    
    source: Optional[str] = Field(None, description="Filter by source")
    symbol: Optional[str] = Field(None, description="Filter by symbol")


class RequestMetadata(BaseModel):
    """Request metadata."""
    
    request_id: str
    api_latency_ms: float
    page: int
    page_size: int
    total_count: int


class DataResponse(BaseModel):
    """Generic data response with metadata."""
    
    data: List[Any]
    metadata: RequestMetadata


class HealthStatus(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Overall status")
    database: str = Field(..., description="Database connection status")
    etl_status: Dict[str, Any] = Field(..., description="ETL status details")


class ETLSourceStats(BaseModel):
    """ETL statistics for a single source."""
    
    source: str
    total_runs: int
    records_processed: int
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    average_duration_seconds: float
    success_rate: float


class StatsResponse(BaseModel):
    """ETL statistics response."""
    
    total_runs: int
    records_processed: int
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    average_duration_seconds: float
    by_source: Dict[str, ETLSourceStats]


class ETLRunResponse(BaseModel):
    """ETL run details."""
    
    run_id: str
    source: str
    status: str
    records_processed: int
    duration_seconds: Optional[float]
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Error response."""
    
    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None
