"""Pydantic schemas for cryptocurrency data."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class CoinBase(BaseModel):
    """Base coin schema."""
    
    coin_id: str = Field(..., min_length=1, description="Unique coin identifier")
    symbol: str = Field(..., min_length=1, description="Coin symbol (e.g., BTC, ETH)")
    name: str = Field(..., min_length=1, description="Coin name")
    current_price: Optional[float] = Field(None, description="Current price in USD")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    volume_24h: Optional[float] = Field(None, description="24h trading volume")
    price_change_24h: Optional[float] = Field(None, description="24h price change percentage")
    rank: Optional[int] = Field(None, description="Market cap rank")
    
    @validator('symbol')
    def symbol_uppercase(cls, v):
        """Convert symbol to uppercase."""
        return v.upper() if v else v
    
    @validator('current_price', 'market_cap', 'volume_24h', 'price_change_24h')
    def validate_numeric(cls, v):
        """Validate numeric fields."""
        if v is not None and v < 0:
            return None
        return v


class CoinCreate(CoinBase):
    """Schema for creating a coin."""
    
    source: str = Field(..., description="Data source")
    last_updated: Optional[datetime] = None


class CoinResponse(CoinBase):
    """Schema for coin response."""
    
    id: int
    source: str
    last_updated: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CoinPaprikaRaw(BaseModel):
    """Schema for CoinPaprika raw data."""
    
    id: str
    name: str
    symbol: str
    rank: int
    circulating_supply: Optional[float] = None
    total_supply: Optional[float] = None
    max_supply: Optional[float] = None
    beta_value: Optional[float] = None
    
    class Config:
        extra = 'allow'


class CoinGeckoRaw(BaseModel):
    """Schema for CoinGecko raw data."""
    
    id: str
    symbol: str
    name: str
    current_price: Optional[float] = None
    market_cap: Optional[int] = None
    market_cap_rank: Optional[int] = None
    total_volume: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None
    
    class Config:
        extra = 'allow'


class CSVCoinRaw(BaseModel):
    """Schema for CSV coin data."""
    
    coin_id: str
    symbol: str
    name: str
    price: Optional[float] = None
    market_cap: Optional[float] = None
    volume: Optional[float] = None
    change_24h: Optional[float] = None
    rank: Optional[int] = None
    
    class Config:
        extra = 'allow'
