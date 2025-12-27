"""Base ETL class with common functionality."""
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from core.database import get_db_context
from core.logging import logger
from core.models import ETLCheckpoint, ETLRun
from core.rate_limiter import rate_limiter_registry


class BaseETL(ABC):
    """Base class for ETL operations."""
    
    def __init__(self, source_name: str, rate_limit: int):
        """
        Initialize ETL.
        
        Args:
            source_name: Name of the data source
            rate_limit: Rate limit for API calls (requests per minute)
        """
        self.source_name = source_name
        self.rate_limiter = rate_limiter_registry.get_limiter(source_name, rate_limit)
        self.run_id = str(uuid.uuid4())
        self.started_at = datetime.utcnow()
        self.records_processed = 0
    
    @abstractmethod
    def extract(self) -> List[Dict[str, Any]]:
        """
        Extract data from source.
        
        Returns:
            List of raw data records
        """
        pass
    
    @abstractmethod
    def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform raw data to normalized format.
        
        Args:
            raw_data: Raw data from source
            
        Returns:
            Normalized data records
        """
        pass
    
    @abstractmethod
    def load_raw(self, db: Session, raw_data: List[Dict[str, Any]]) -> None:
        """
        Load raw data into database.
        
        Args:
            db: Database session
            raw_data: Raw data to load
        """
        pass
    
    def load_normalized(self, db: Session, normalized_data: List[Dict[str, Any]]) -> None:
        """
        Load normalized data into database using upsert.
        
        Args:
            db: Database session
            normalized_data: Normalized data to load
        """
        from core.models import Coin
        
        if not normalized_data:
            return
        
        # Upsert data (idempotent)
        stmt = insert(Coin).values(normalized_data)
        stmt = stmt.on_conflict_do_update(
            index_elements=['coin_id', 'source'],
            set_={
                'name': stmt.excluded.name,
                'symbol': stmt.excluded.symbol,
                'current_price': stmt.excluded.current_price,
                'market_cap': stmt.excluded.market_cap,
                'volume_24h': stmt.excluded.volume_24h,
                'price_change_24h': stmt.excluded.price_change_24h,
                'rank': stmt.excluded.rank,
                'last_updated': stmt.excluded.last_updated,
                'updated_at': datetime.utcnow(),
            }
        )
        db.execute(stmt)
        self.records_processed += len(normalized_data)
    
    def update_checkpoint(self, db: Session, status: str, error_message: Optional[str] = None) -> None:
        """
        Update ETL checkpoint.
        
        Args:
            db: Database session
            status: Execution status
            error_message: Error message if failed
        """
        now = datetime.utcnow()
        
        checkpoint = db.query(ETLCheckpoint).filter(
            ETLCheckpoint.source == self.source_name
        ).first()
        
        if checkpoint:
            checkpoint.last_run_at = now
            checkpoint.status = status
            checkpoint.records_processed = self.records_processed
            checkpoint.updated_at = now
            
            if status == 'success':
                checkpoint.last_success_at = now
                checkpoint.error_message = None
            elif status == 'failure':
                checkpoint.last_failure_at = now
                checkpoint.error_message = error_message
        else:
            checkpoint = ETLCheckpoint(
                source=self.source_name,
                last_run_at=now,
                status=status,
                records_processed=self.records_processed,
                last_success_at=now if status == 'success' else None,
                last_failure_at=now if status == 'failure' else None,
                error_message=error_message
            )
            db.add(checkpoint)
    
    def create_run_record(self, db: Session, status: str, error_message: Optional[str] = None) -> None:
        """
        Create ETL run record.
        
        Args:
            db: Database session
            status: Execution status
            error_message: Error message if failed
        """
        completed_at = datetime.utcnow()
        duration = (completed_at - self.started_at).total_seconds()
        
        run = ETLRun(
            run_id=self.run_id,
            source=self.source_name,
            status=status,
            records_processed=self.records_processed,
            duration_seconds=duration,
            started_at=self.started_at,
            completed_at=completed_at,
            error_message=error_message
        )
        db.add(run)
    
    def run(self, max_retries: int = 3, backoff_factor: float = 2.0) -> bool:
        """
        Execute full ETL pipeline with retry logic.
        
        Args:
            max_retries: Maximum number of retries
            backoff_factor: Exponential backoff factor
            
        Returns:
            True if successful, False otherwise
        """
        attempt = 0
        last_error = None
        
        while attempt < max_retries:
            try:
                logger.info(
                    f"Starting ETL run for {self.source_name}",
                    extra={"source": self.source_name, "run_id": self.run_id, "attempt": attempt + 1}
                )
                
                with get_db_context() as db:
                    # Extract
                    logger.info(f"Extracting data from {self.source_name}")
                    raw_data = self.extract()
                    logger.info(f"Extracted {len(raw_data)} records from {self.source_name}")
                    
                    # Load raw
                    logger.info(f"Loading raw data for {self.source_name}")
                    self.load_raw(db, raw_data)
                    
                    # Transform
                    logger.info(f"Transforming data for {self.source_name}")
                    normalized_data = self.transform(raw_data)
                    logger.info(f"Transformed {len(normalized_data)} records for {self.source_name}")
                    
                    # Load normalized
                    logger.info(f"Loading normalized data for {self.source_name}")
                    self.load_normalized(db, normalized_data)
                    
                    # Update checkpoint
                    self.update_checkpoint(db, 'success')
                    
                    # Create run record
                    self.create_run_record(db, 'success')
                    
                    logger.info(
                        f"ETL run completed successfully for {self.source_name}",
                        extra={
                            "source": self.source_name,
                            "run_id": self.run_id,
                            "records_processed": self.records_processed
                        }
                    )
                    
                    return True
                    
            except Exception as e:
                last_error = str(e)
                attempt += 1
                
                logger.error(
                    f"ETL run failed for {self.source_name}: {e}",
                    extra={
                        "source": self.source_name,
                        "run_id": self.run_id,
                        "attempt": attempt,
                        "error": str(e)
                    },
                    exc_info=True
                )
                
                if attempt < max_retries:
                    wait_time = backoff_factor ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        
        # All retries failed
        try:
            with get_db_context() as db:
                self.update_checkpoint(db, 'failure', last_error)
                self.create_run_record(db, 'failure', last_error)
        except Exception as e:
            logger.error(f"Failed to update checkpoint: {e}")
        
        return False
