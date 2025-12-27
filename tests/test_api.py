"""Tests for API endpoints."""
import pytest
from datetime import datetime


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert data["status"] == "running"


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "etl_status" in data


def test_data_endpoint_default(client, db_session, sample_coin_data):
    """Test data endpoint with default parameters."""
    from core.models import Coin
    
    # Insert test data
    for coin_data in sample_coin_data:
        coin = Coin(**coin_data, last_updated=datetime.utcnow())
        db_session.add(coin)
    db_session.commit()
    
    response = client.get("/data")
    assert response.status_code == 200
    data = response.json()
    
    assert "data" in data
    assert "metadata" in data
    assert "request_id" in data["metadata"]
    assert "api_latency_ms" in data["metadata"]
    assert data["metadata"]["page"] == 1
    assert data["metadata"]["page_size"] == 50


def test_data_endpoint_pagination(client, db_session, sample_coin_data):
    """Test data endpoint pagination."""
    from core.models import Coin
    
    # Insert test data
    for coin_data in sample_coin_data:
        coin = Coin(**coin_data, last_updated=datetime.utcnow())
        db_session.add(coin)
    db_session.commit()
    
    response = client.get("/data?page=1&page_size=1")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["data"]) <= 1
    assert data["metadata"]["page"] == 1
    assert data["metadata"]["page_size"] == 1


def test_data_endpoint_filter_by_source(client, db_session, sample_coin_data):
    """Test data endpoint filtering by source."""
    from core.models import Coin
    
    # Insert test data
    for coin_data in sample_coin_data:
        coin = Coin(**coin_data, last_updated=datetime.utcnow())
        db_session.add(coin)
    db_session.commit()
    
    response = client.get("/data?source=test")
    assert response.status_code == 200
    data = response.json()
    
    # All returned coins should be from 'test' source
    for coin in data["data"]:
        assert coin["source"] == "test"


def test_data_endpoint_filter_by_symbol(client, db_session, sample_coin_data):
    """Test data endpoint filtering by symbol."""
    from core.models import Coin
    
    # Insert test data
    for coin_data in sample_coin_data:
        coin = Coin(**coin_data, last_updated=datetime.utcnow())
        db_session.add(coin)
    db_session.commit()
    
    response = client.get("/data?symbol=BTC")
    assert response.status_code == 200
    data = response.json()
    
    # Should only return Bitcoin
    if len(data["data"]) > 0:
        assert all(coin["symbol"] == "BTC" for coin in data["data"])


def test_stats_endpoint(client, db_session):
    """Test stats endpoint."""
    from core.models import ETLRun
    
    # Insert test ETL run
    run = ETLRun(
        run_id='test-run-123',
        source='test_source',
        status='success',
        records_processed=100,
        duration_seconds=10.5,
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow()
    )
    db_session.add(run)
    db_session.commit()
    
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    
    assert "total_runs" in data
    assert "records_processed" in data
    assert "average_duration_seconds" in data
    assert "by_source" in data


def test_data_endpoint_invalid_page(client):
    """Test data endpoint with invalid page number."""
    response = client.get("/data?page=0")
    assert response.status_code == 422  # Validation error


def test_data_endpoint_invalid_page_size(client):
    """Test data endpoint with invalid page size."""
    response = client.get("/data?page_size=200")
    assert response.status_code == 422  # Validation error (exceeds max of 100)


def test_api_latency_metadata(client, db_session, sample_coin_data):
    """Test that API latency is included in metadata."""
    from core.models import Coin
    
    # Insert test data
    for coin_data in sample_coin_data:
        coin = Coin(**coin_data, last_updated=datetime.utcnow())
        db_session.add(coin)
    db_session.commit()
    
    response = client.get("/data")
    assert response.status_code == 200
    data = response.json()
    
    assert "api_latency_ms" in data["metadata"]
    assert isinstance(data["metadata"]["api_latency_ms"], (int, float))
    assert data["metadata"]["api_latency_ms"] >= 0


def test_request_id_in_response(client):
    """Test that request ID is included in response headers."""
    response = client.get("/health")
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0
