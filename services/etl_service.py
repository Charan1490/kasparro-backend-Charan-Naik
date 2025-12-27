"""ETL service orchestration."""
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from ingestion.coinpaprika import CoinPaprikaETL
from ingestion.coingecko import CoinGeckoETL
from ingestion.csv_source import CSVSourceETL
from core.logging import logger


class ETLService:
    """Service for orchestrating ETL operations."""
    
    def __init__(self):
        """Initialize ETL service."""
        self.etl_sources = {
            'coinpaprika': CoinPaprikaETL,
            'coingecko': CoinGeckoETL,
            'csv': CSVSourceETL
        }
    
    def run_single_source(self, source_name: str) -> bool:
        """
        Run ETL for a single source.
        
        Args:
            source_name: Name of the data source
            
        Returns:
            True if successful, False otherwise
        """
        if source_name not in self.etl_sources:
            logger.error(f"Unknown ETL source: {source_name}")
            return False
        
        etl_class = self.etl_sources[source_name]
        etl = etl_class()
        return etl.run()
    
    def run_all_sources(self, parallel: bool = True) -> Dict[str, bool]:
        """
        Run ETL for all sources.
        
        Args:
            parallel: Whether to run sources in parallel
            
        Returns:
            Dictionary mapping source names to success status
        """
        results = {}
        
        if parallel:
            # Run in parallel
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_to_source = {
                    executor.submit(self.run_single_source, source): source
                    for source in self.etl_sources.keys()
                }
                
                for future in as_completed(future_to_source):
                    source = future_to_source[future]
                    try:
                        results[source] = future.result()
                    except Exception as e:
                        logger.error(f"Failed to run ETL for {source}: {e}")
                        results[source] = False
        else:
            # Run sequentially
            for source in self.etl_sources.keys():
                results[source] = self.run_single_source(source)
        
        return results
    
    def get_etl_status(self) -> Dict[str, Any]:
        """
        Get current ETL status for all sources.
        
        Returns:
            Dictionary with ETL status information
        """
        from core.database import get_db_context
        from core.models import ETLCheckpoint
        
        with get_db_context() as db:
            checkpoints = db.query(ETLCheckpoint).all()
            
            status = {}
            for checkpoint in checkpoints:
                status[checkpoint.source] = {
                    'last_run': checkpoint.last_run_at.isoformat() if checkpoint.last_run_at else None,
                    'last_success': checkpoint.last_success_at.isoformat() if checkpoint.last_success_at else None,
                    'last_failure': checkpoint.last_failure_at.isoformat() if checkpoint.last_failure_at else None,
                    'status': checkpoint.status,
                    'records_processed': checkpoint.records_processed,
                    'error_message': checkpoint.error_message
                }
            
            return status
