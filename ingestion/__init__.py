"""Ingestion package initialization."""
from ingestion.coinpaprika import CoinPaprikaETL
from ingestion.coingecko import CoinGeckoETL
from ingestion.csv_source import CSVSourceETL

__all__ = ['CoinPaprikaETL', 'CoinGeckoETL', 'CSVSourceETL']
