"""SQLAlchemy ORM models."""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, 
    Boolean, Text, JSON, Index, UniqueConstraint
)

from core.database import Base


class RawCoinPaprika(Base):
    """Raw data from CoinPaprika API."""
    
    __tablename__ = "raw_coinpaprika"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(String(100), nullable=False)
    raw_data = Column(JSON, nullable=False)
    ingested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_coinpaprika_coin_id', 'coin_id'),
        Index('idx_coinpaprika_ingested_at', 'ingested_at'),
    )


class RawCoinGecko(Base):
    """Raw data from CoinGecko API."""
    
    __tablename__ = "raw_coingecko"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(String(100), nullable=False)
    raw_data = Column(JSON, nullable=False)
    ingested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_coingecko_coin_id', 'coin_id'),
        Index('idx_coingecko_ingested_at', 'ingested_at'),
    )


class RawCSV(Base):
    """Raw data from CSV source."""
    
    __tablename__ = "raw_csv"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(String(100), nullable=False)
    raw_data = Column(JSON, nullable=False)
    ingested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_csv_coin_id', 'coin_id'),
        Index('idx_csv_ingested_at', 'ingested_at'),
    )


class Coin(Base):
    """Normalized cryptocurrency data."""
    
    __tablename__ = "coins"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    coin_id = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False)
    name = Column(String(200), nullable=False)
    current_price = Column(Float, nullable=True)
    market_cap = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    price_change_24h = Column(Float, nullable=True)
    source = Column(String(50), nullable=False)  # coinpaprika, coingecko, csv
    rank = Column(Integer, nullable=True)
    last_updated = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('coin_id', 'source', name='uq_coin_source'),
        Index('idx_coins_symbol', 'symbol'),
        Index('idx_coins_source', 'source'),
        Index('idx_coins_rank', 'rank'),
    )


class ETLCheckpoint(Base):
    """ETL execution checkpoints for resumption."""
    
    __tablename__ = "etl_checkpoints"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False, unique=True)
    last_run_at = Column(DateTime, nullable=True)
    last_success_at = Column(DateTime, nullable=True)
    last_failure_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False)  # success, failure, running
    records_processed = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    run_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_checkpoint_source', 'source'),
        Index('idx_checkpoint_status', 'status'),
    )


class ETLRun(Base):
    """ETL run history and metrics."""
    
    __tablename__ = "etl_runs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(100), nullable=False, unique=True)
    source = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)  # success, failure, running
    records_processed = Column(Integer, default=0)
    duration_seconds = Column(Float, nullable=True)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    run_metadata = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('idx_run_source', 'source'),
        Index('idx_run_status', 'status'),
        Index('idx_run_started_at', 'started_at'),
    )
