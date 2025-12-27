"""Pytest configuration and fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from core.database import Base, get_db
from core.config import get_settings
from api.main import app

settings = get_settings()

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """Create test database session."""
    # Clear all tables before each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with test database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_coin_data():
    """Sample cryptocurrency data for testing."""
    return [
        {
            'coin_id': 'bitcoin',
            'symbol': 'BTC',
            'name': 'Bitcoin',
            'current_price': 43000.0,
            'market_cap': 840000000000.0,
            'volume_24h': 28000000000.0,
            'price_change_24h': 2.5,
            'rank': 1,
            'source': 'test'
        },
        {
            'coin_id': 'ethereum',
            'symbol': 'ETH',
            'name': 'Ethereum',
            'current_price': 2250.0,
            'market_cap': 270000000000.0,
            'volume_24h': 15000000000.0,
            'price_change_24h': 1.8,
            'rank': 2,
            'source': 'test'
        }
    ]
