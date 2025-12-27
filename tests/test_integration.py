"""Integration tests for end-to-end workflows."""
import pytest
from datetime import datetime


def test_full_etl_to_api_workflow(client, db_session):
    """Test complete workflow from ETL to API retrieval."""
    from core.models import Coin, ETLRun, ETLCheckpoint
    
    # Simulate ETL run
    run = ETLRun(
        run_id='integration-test-run',
        source='test',
        status='success',
        records_processed=2,
        duration_seconds=5.0,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow()
    )
    db_session.add(run)
    
    # Create checkpoint
    checkpoint = ETLCheckpoint(
        source='test',
        last_run_at=datetime.utcnow(),
        last_success_at=datetime.utcnow(),
        status='success',
        records_processed=2
    )
    db_session.add(checkpoint)
    
    # Insert coins
    coins = [
        Coin(
            coin_id='bitcoin',
            symbol='BTC',
            name='Bitcoin',
            current_price=43000.0,
            market_cap=840000000000.0,
            volume_24h=28000000000.0,
            price_change_24h=2.5,
            rank=1,
            source='test',
            last_updated=datetime.utcnow()
        ),
        Coin(
            coin_id='ethereum',
            symbol='ETH',
            name='Ethereum',
            current_price=2250.0,
            market_cap=270000000000.0,
            volume_24h=15000000000.0,
            price_change_24h=1.8,
            rank=2,
            source='test',
            last_updated=datetime.utcnow()
        )
    ]
    
    for coin in coins:
        db_session.add(coin)
    
    db_session.commit()
    
    # Test health endpoint shows success
    health_response = client.get("/health")
    assert health_response.status_code == 200
    health_data = health_response.json()
    assert health_data["database"] == "connected"
    
    # Test data endpoint returns coins
    data_response = client.get("/data")
    assert data_response.status_code == 200
    data = data_response.json()
    assert len(data["data"]) == 2
    
    # Test stats endpoint shows metrics
    stats_response = client.get("/stats")
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["total_runs"] >= 1
    assert stats["records_processed"] >= 2


def test_rate_limiting_logic():
    """Test rate limiter functionality."""
    from core.rate_limiter import RateLimiter
    import time
    
    # Use a very low rate limit for testing (1 request per minute = very restrictive)
    limiter = RateLimiter(rate_limit=1)
    
    # First request should succeed
    assert limiter.acquire() is True
    
    # Second request immediately after should fail (no tokens left)
    assert limiter.acquire() is False
    
    # Third request should also fail
    assert limiter.acquire() is False


def test_schema_validation_edge_cases():
    """Test schema validation with edge cases."""
    from schemas.coin import CoinCreate
    
    # Test with minimal required fields
    minimal_coin = CoinCreate(
        coin_id='test',
        symbol='TST',
        name='Test Coin',
        source='test'
    )
    
    assert minimal_coin.coin_id == 'test'
    assert minimal_coin.symbol == 'TST'
    assert minimal_coin.current_price is None
    
    # Test with all fields
    full_coin = CoinCreate(
        coin_id='bitcoin',
        symbol='btc',
        name='Bitcoin',
        current_price=43000.0,
        market_cap=840000000000.0,
        volume_24h=28000000000.0,
        price_change_24h=2.5,
        rank=1,
        source='test'
    )
    
    assert full_coin.symbol == 'BTC'  # Should be uppercased
    assert full_coin.current_price == 43000.0


def test_database_connection_handling(db_session):
    """Test database connection and error handling."""
    from core.models import Coin
    
    # Test valid insert
    coin = Coin(
        coin_id='test-db-conn',
        symbol='TDB',
        name='Test DB Connection',
        source='test',
        last_updated=datetime.utcnow()
    )
    
    db_session.add(coin)
    db_session.commit()
    
    # Test retrieval
    retrieved = db_session.query(Coin).filter(
        Coin.coin_id == 'test-db-conn'
    ).first()
    
    assert retrieved is not None
    assert retrieved.symbol == 'TDB'


def test_concurrent_etl_runs(db_session):
    """Test handling of concurrent ETL runs."""
    from core.models import ETLRun
    from datetime import datetime, timedelta
    
    # Simulate multiple concurrent runs
    run1 = ETLRun(
        run_id='concurrent-run-1',
        source='source1',
        status='success',
        records_processed=100,
        duration_seconds=10.0,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow()
    )
    
    run2 = ETLRun(
        run_id='concurrent-run-2',
        source='source2',
        status='success',
        records_processed=150,
        duration_seconds=12.0,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow()
    )
    
    db_session.add(run1)
    db_session.add(run2)
    db_session.commit()
    
    # Verify both runs were recorded
    runs = db_session.query(ETLRun).filter(
        ETLRun.run_id.in_(['concurrent-run-1', 'concurrent-run-2'])
    ).all()
    
    assert len(runs) == 2
