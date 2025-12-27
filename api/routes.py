"""API route handlers."""
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from core.database import get_db, check_db_connection
from services.data_service import DataService
from services.etl_service import ETLService
from schemas.api_models import DataResponse, HealthStatus, RequestMetadata

router = APIRouter()
data_service = DataService()
etl_service = ETLService()


@router.get("/data", response_model=DataResponse)
async def get_data(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    source: Optional[str] = Query(None, description="Filter by source (coinpaprika, coingecko, csv)"),
    symbol: Optional[str] = Query(None, description="Filter by symbol (e.g., BTC, ETH)"),
    db: Session = Depends(get_db)
):
    """
    Get cryptocurrency data with pagination and filtering.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 50, max: 100)
    - **source**: Filter by data source
    - **symbol**: Filter by cryptocurrency symbol
    """
    start_time = time.time()
    
    try:
        coins, total_count = data_service.get_coins(
            db=db,
            page=page,
            page_size=page_size,
            source=source,
            symbol=symbol
        )
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        metadata = RequestMetadata(
            request_id=request.state.request_id,
            api_latency_ms=round(latency_ms, 2),
            page=page,
            page_size=page_size,
            total_count=total_count
        )
        
        return DataResponse(
            data=[coin.model_dump() for coin in coins],
            metadata=metadata.model_dump()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve data: {str(e)}")


@router.get("/health", response_model=HealthStatus)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    
    Reports:
    - Overall system status
    - Database connectivity
    - ETL last-run status for each source
    """
    # Check database using the injected session
    db_status = "disconnected"
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        pass
    
    # Get ETL status
    etl_status_data = etl_service.get_etl_status()
    
    # Determine overall status
    overall_status = "healthy" if db_status == "connected" else "unhealthy"
    
    # Check if any ETL source has failed recently
    sources_status = {}
    for source, status in etl_status_data.items():
        sources_status[source] = status.get('status', 'unknown')
        if status.get('status') == 'failure':
            overall_status = "degraded"
    
    etl_status = {
        "last_run": None,
        "status": "unknown",
        "sources": sources_status
    }
    
    # Get most recent run
    if etl_status_data:
        latest_run = None
        for source, status in etl_status_data.items():
            if status.get('last_run'):
                if not latest_run or status['last_run'] > latest_run:
                    latest_run = status['last_run']
        
        if latest_run:
            etl_status["last_run"] = latest_run
            # Determine overall ETL status
            if all(s == 'success' for s in sources_status.values()):
                etl_status["status"] = "success"
            elif any(s == 'failure' for s in sources_status.values()):
                etl_status["status"] = "partial_failure"
            else:
                etl_status["status"] = "running"
    
    return HealthStatus(
        status=overall_status,
        database=db_status,
        etl_status=etl_status
    )


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """
    Get ETL execution statistics.
    
    Returns:
    - Total runs across all sources
    - Records processed
    - Last success/failure timestamps
    - Average duration
    - Per-source breakdown
    """
    try:
        stats = data_service.get_etl_stats(db)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stats: {str(e)}")


@router.post("/etl/run")
async def trigger_etl(
    source: Optional[str] = Query(None, description="Specific source to run (leave empty for all)")
):
    """
    Manually trigger ETL execution.
    
    - **source**: Optional - Run ETL for specific source (coinpaprika, coingecko, csv)
    - If no source specified, runs all sources
    """
    try:
        if source:
            # Run specific source
            success = etl_service.run_single_source(source)
            return {
                "message": f"ETL triggered for {source}",
                "success": success
            }
        else:
            # Run all sources
            results = etl_service.run_all_sources(parallel=True)
            return {
                "message": "ETL triggered for all sources",
                "results": results
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger ETL: {str(e)}")
