"""CSV source ETL implementation."""
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from ingestion.base import BaseETL
from core.config import get_settings
from core.models import RawCSV
from schemas.coin import CoinCreate

settings = get_settings()


class CSVSourceETL(BaseETL):
    """ETL for CSV data source."""
    
    def __init__(self, csv_path: str = "data/crypto_data.csv"):
        """
        Initialize CSV ETL.
        
        Args:
            csv_path: Path to CSV file
        """
        super().__init__("csv", settings.csv_batch_size)
        self.csv_path = Path(csv_path)
    
    def extract(self) -> List[Dict[str, Any]]:
        """
        Extract data from CSV file.
        
        Returns:
            List of raw coin data
        """
        if not self.csv_path.exists():
            from core.logging import logger
            logger.warning(f"CSV file not found: {self.csv_path}")
            return []
        
        data = []
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(dict(row))
        
        return data
    
    def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform CSV data to normalized format.
        
        Args:
            raw_data: Raw data from CSV
            
        Returns:
            Normalized coin data
        """
        normalized = []
        
        for item in raw_data:
            try:
                # Clean and convert data types
                coin_data = {
                    'coin_id': item.get('coin_id', item.get('id', '')),
                    'symbol': str(item.get('symbol', '')).upper(),
                    'name': item.get('name', ''),
                    'current_price': self._parse_float(item.get('price', item.get('current_price'))),
                    'market_cap': self._parse_float(item.get('market_cap')),
                    'volume_24h': self._parse_float(item.get('volume', item.get('volume_24h'))),
                    'price_change_24h': self._parse_float(item.get('change_24h', item.get('price_change_24h'))),
                    'rank': self._parse_int(item.get('rank')),
                    'source': 'csv',
                    'last_updated': datetime.utcnow()
                }
                
                # Validate using Pydantic
                validated = CoinCreate(**coin_data)
                normalized.append(validated.model_dump())
                
            except Exception as e:
                # Log and skip invalid records
                from core.logging import logger
                logger.warning(
                    f"Failed to transform CSV record: {e}",
                    extra={"record": item, "error": str(e)}
                )
                continue
        
        return normalized
    
    def load_raw(self, db: Session, raw_data: List[Dict[str, Any]]) -> None:
        """
        Load raw data into database.
        
        Args:
            db: Database session
            raw_data: Raw data to load
        """
        for item in raw_data:
            raw_record = RawCSV(
                coin_id=item.get('coin_id', item.get('id', 'unknown')),
                raw_data=item,
                ingested_at=datetime.utcnow()
            )
            db.add(raw_record)
    
    @staticmethod
    def _parse_float(value: Any) -> float:
        """Parse float value safely."""
        if value is None or value == '':
            return None
        try:
            return float(str(value).replace(',', '').replace('$', ''))
        except (ValueError, AttributeError):
            return None
    
    @staticmethod
    def _parse_int(value: Any) -> int:
        """Parse integer value safely."""
        if value is None or value == '':
            return None
        try:
            return int(float(str(value)))
        except (ValueError, AttributeError):
            return None
