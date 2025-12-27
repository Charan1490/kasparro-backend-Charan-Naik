"""CoinGecko API ETL implementation."""
from datetime import datetime
from typing import List, Dict, Any

import httpx
from sqlalchemy.orm import Session

from ingestion.base import BaseETL
from core.config import get_settings
from core.models import RawCoinGecko
from schemas.coin import CoinCreate

settings = get_settings()


class CoinGeckoETL(BaseETL):
    """ETL for CoinGecko API."""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self):
        """Initialize CoinGecko ETL."""
        super().__init__("coingecko", settings.coingecko_rate_limit)
        self.api_key = settings.coingecko_api_key
    
    def extract(self) -> List[Dict[str, Any]]:
        """
        Extract data from CoinGecko API.
        
        Returns:
            List of raw coin data
        """
        # Rate limiting
        self.rate_limiter.wait()
        
        headers = {}
        if self.api_key:
            headers['x-cg-demo-api-key'] = self.api_key
        
        # Get top coins by market cap
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{self.BASE_URL}/coins/markets",
                headers=headers,
                params={
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": 100,
                    "page": 1,
                    "sparkline": False
                }
            )
            response.raise_for_status()
            return response.json()
    
    def transform(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform CoinGecko data to normalized format.
        
        Args:
            raw_data: Raw data from CoinGecko
            
        Returns:
            Normalized coin data
        """
        normalized = []
        
        for item in raw_data:
            try:
                coin_data = {
                    'coin_id': item.get('id', ''),
                    'symbol': item.get('symbol', '').upper(),
                    'name': item.get('name', ''),
                    'current_price': item.get('current_price'),
                    'market_cap': item.get('market_cap'),
                    'volume_24h': item.get('total_volume'),
                    'price_change_24h': item.get('price_change_percentage_24h'),
                    'rank': item.get('market_cap_rank'),
                    'source': 'coingecko',
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
            raw_record = RawCoinGecko(
                coin_id=item.get('id', 'unknown'),
                raw_data=item,
                ingested_at=datetime.utcnow()
            )
            db.add(raw_record)
