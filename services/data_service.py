"""Data retrieval service."""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from core.models import Coin, ETLRun
from schemas.coin import CoinResponse


class DataService:
    """Service for retrieving cryptocurrency data."""
    
    @staticmethod
    def get_coins(
        db: Session,
        page: int = 1,
        page_size: int = 50,
        source: Optional[str] = None,
        symbol: Optional[str] = None
    ) -> Tuple[List[CoinResponse], int]:
        """
        Get paginated and filtered coin data.
        
        Args:
            db: Database session
            page: Page number
            page_size: Items per page
            source: Filter by source
            symbol: Filter by symbol
            
        Returns:
            Tuple of (coins, total_count)
        """
        query = db.query(Coin)
        
        # Apply filters
        if source:
            query = query.filter(Coin.source == source.lower())
        if symbol:
            query = query.filter(Coin.symbol == symbol.upper())
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        coins = query.order_by(desc(Coin.rank)).offset(offset).limit(page_size).all()
        
        return [CoinResponse.model_validate(coin) for coin in coins], total_count
    
    @staticmethod
    def get_etl_stats(db: Session) -> dict:
        """
        Get ETL execution statistics.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with statistics
        """
        # Overall stats
        total_runs = db.query(func.count(ETLRun.id)).scalar() or 0
        total_records = db.query(func.sum(ETLRun.records_processed)).scalar() or 0
        avg_duration = db.query(func.avg(ETLRun.duration_seconds)).filter(
            ETLRun.status == 'success'
        ).scalar() or 0
        
        # Last success/failure
        last_success = db.query(ETLRun).filter(
            ETLRun.status == 'success'
        ).order_by(desc(ETLRun.completed_at)).first()
        
        last_failure = db.query(ETLRun).filter(
            ETLRun.status == 'failure'
        ).order_by(desc(ETLRun.completed_at)).first()
        
        # Per-source stats
        by_source = {}
        sources = ['coinpaprika', 'coingecko', 'csv']
        
        for source in sources:
            source_runs = db.query(func.count(ETLRun.id)).filter(
                ETLRun.source == source
            ).scalar() or 0
            
            source_records = db.query(func.sum(ETLRun.records_processed)).filter(
                ETLRun.source == source
            ).scalar() or 0
            
            source_avg_duration = db.query(func.avg(ETLRun.duration_seconds)).filter(
                ETLRun.source == source,
                ETLRun.status == 'success'
            ).scalar() or 0
            
            source_last_success = db.query(ETLRun).filter(
                ETLRun.source == source,
                ETLRun.status == 'success'
            ).order_by(desc(ETLRun.completed_at)).first()
            
            source_last_failure = db.query(ETLRun).filter(
                ETLRun.source == source,
                ETLRun.status == 'failure'
            ).order_by(desc(ETLRun.completed_at)).first()
            
            success_count = db.query(func.count(ETLRun.id)).filter(
                ETLRun.source == source,
                ETLRun.status == 'success'
            ).scalar() or 0
            
            success_rate = (success_count / source_runs * 100) if source_runs > 0 else 0
            
            by_source[source] = {
                'source': source,
                'total_runs': source_runs,
                'records_processed': source_records,
                'average_duration_seconds': round(source_avg_duration, 2),
                'success_rate': round(success_rate, 2),
                'last_success': source_last_success.completed_at.isoformat() if source_last_success and source_last_success.completed_at else None,
                'last_failure': source_last_failure.completed_at.isoformat() if source_last_failure and source_last_failure.completed_at else None
            }
        
        return {
            'total_runs': total_runs,
            'records_processed': total_records,
            'average_duration_seconds': round(avg_duration, 2),
            'last_success': last_success.completed_at.isoformat() if last_success and last_success.completed_at else None,
            'last_failure': last_failure.completed_at.isoformat() if last_failure and last_failure.completed_at else None,
            'by_source': by_source
        }
