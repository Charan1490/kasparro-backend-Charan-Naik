"""CoinPaprika API ETL implementation."""
from datetime import datetime
from typing import List, Dict, Any

import httpx
from sqlalchemy.orm import Session

from ingestion.base import BaseETL
from core.config import get_settings
from core.models import RawCoinPaprika
from schemas.coin import CoinCreate

settings = get_settings()


class CoinPaprikaETL(BaseETL):
    """ETL for CoinPaprika API."""
    
    BASE_URL = "https://api.coinpaprika.com/v1"
    
    def __init__(self):
        """Initialize CoinPaprika ETL."""
        super().__init__("coinpaprika", settings.coinpaprika_rate_limit)
    
    def extract(self) -> List[Dict[str, Any]]:
        """
        Extract data from CoinPaprika API.
        
        CoinPaprika free tier does not require API key.
        Rate limit: 10 requests per second (we use 10 per minute to be safe).
        
        Returns:
            List of raw coin data
        """
        # Rate limiting
        self.rate_limiter.wait()
        
        # CoinPaprika free tier - no authentication needed
        # Get top 100 coins by market cap
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{self.BASE_URL}/tickers",
                params={"limit": 100}
            )
            response.raise_for_status()
            return response.json()
    
    def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform CoinPaprika data to normalized format.
        
        Args:
            raw_data: Raw data from CoinPaprika
            
        Returns:
            Normalized coin data
        """
        normalized = []
        
        for item in raw_data:
            try:
                quotes = item.get('quotes', {}).get('USD', {})
                
                coin_data = {
                    'coin_id': item.get('id', ''),
                    'symbol': item.get('symbol', '').upper(),
                    'name': item.get('name', ''),
                    'current_price': quotes.get('price'),
                    'market_cap': quotes.get('market_cap'),
                    'volume_24h': quotes.get('volume_24h'),
                    'price_change_24h': quotes.get('percent_change_24h'),
                    'rank': item.get('rank'),
                    'source': 'coinpaprika',
                    'last_updated': datetime.utcnow()
                }
                
                # Validate using Pydantic
                validated = CoinCreate(**coin_data)
                normalized.append(validated.model_dump())
                
            except Exception as e:
                # Log and skip invalid records
                from core.logging import logger
                logger.warning(
                    f"Failed to transform record: {e}",
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
            raw_record = RawCoinPaprika(
                coin_id=item.get('id', 'unknown'),
                raw_data=item,
                ingested_at=datetime.utcnow()
            )
            db.add(raw_record)
