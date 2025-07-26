import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import datetime

from backend.app.main import app
from backend.app.database import create_tables, drop_tables

@pytest.fixture(scope="function")
def setup_test_db():
    """Set up test database"""
    create_tables()
    yield
    drop_tables()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_kline_response():
    return [
        {
            "time": "2023-12-01T09:30:00",
            "open": 100.0,
            "high": 105.0,
            "low": 98.0,
            "close": 102.0,
            "volume": 1000
        },
        {
            "time": "2023-12-01T09:31:00",
            "open": 102.0,
            "high": 106.0,
            "low": 101.0,
            "close": 104.0,
            "volume": 1200
        }
    ]

def test_get_kline_data_basic(setup_test_db, client, sample_kline_response):
    """Test basic K-line data endpoint"""
    
    with patch('backend.app.api.market_data.data_cache_service') as mock_cache:
        mock_cache.get_kline_data = AsyncMock(return_value=sample_kline_response)
        
        response = client.get("/api/market-data/kline/000001?timeframe=1m")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["symbol"] == "000001"
        assert data["timeframe"] == "1m"
        assert data["count"] == 2
        assert len(data["data"]) == 2
        assert data["data"][0]["open"] == 100.0
        assert data["data"][1]["close"] == 104.0

def test_get_kline_data_with_time_range(setup_test_db, client, sample_kline_response):
    """Test K-line data endpoint with time range"""
    
    with patch('backend.app.api.market_data.data_cache_service') as mock_cache:
        mock_cache.get_kline_data = AsyncMock(return_value=sample_kline_response)
        
        response = client.get(
            "/api/market-data/kline/000001"
            "?timeframe=5m"
            "&start_time=2023-12-01T09:30:00"
            "&end_time=2023-12-01T10:00:00"
            "&use_cache=false"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["symbol"] == "000001"
        assert data["timeframe"] == "5m"
        
        # Verify the service was called with correct parameters
        mock_cache.get_kline_data.assert_called_once()
        call_args = mock_cache.get_kline_data.call_args
        assert call_args.kwargs["symbol"] == "000001"
        assert call_args.kwargs["timeframe"] == "5m"
        assert call_args.kwargs["use_cache"] == False

def test_get_kline_data_invalid_datetime(client):
    """Test K-line data endpoint with invalid datetime format"""
    
    response = client.get(
        "/api/market-data/kline/000001"
        "?start_time=invalid-datetime"
    )
    
    assert response.status_code == 400
    assert "Invalid datetime format" in response.json()["detail"]

def test_get_latest_price(setup_test_db, client):
    """Test latest price endpoint"""
    
    with patch('backend.app.api.market_data.data_cache_service') as mock_cache:
        mock_cache.get_latest_price.return_value = 102.5
        
        response = client.get("/api/market-data/latest-price/000001")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["symbol"] == "000001"
        assert data["price"] == 102.5
        assert "timestamp" in data

def test_get_latest_price_not_found(setup_test_db, client):
    """Test latest price endpoint when no data found"""
    
    with patch('backend.app.api.market_data.data_cache_service') as mock_cache:
        mock_cache.get_latest_price.return_value = None
        
        response = client.get("/api/market-data/latest-price/NONEXISTENT")
        
        assert response.status_code == 404
        assert "No price data found" in response.json()["detail"]

def test_get_available_symbols(client):
    """Test available symbols endpoint"""
    
    response = client.get("/api/market-data/symbols")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "symbols" in data
    assert "count" in data
    assert data["count"] > 0
    
    # Check symbol structure
    first_symbol = data["symbols"][0]
    assert "code" in first_symbol
    assert "name" in first_symbol
    assert "market" in first_symbol

def test_get_available_timeframes(client):
    """Test available timeframes endpoint"""
    
    response = client.get("/api/market-data/timeframes")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "timeframes" in data
    assert "count" in data
    assert data["count"] > 0
    
    # Check timeframe structure
    first_timeframe = data["timeframes"][0]
    assert "code" in first_timeframe
    assert "name" in first_timeframe
    assert "minutes" in first_timeframe
    
    # Verify expected timeframes are present
    codes = [tf["code"] for tf in data["timeframes"]]
    assert "1m" in codes
    assert "5m" in codes
    assert "15m" in codes
    assert "1h" in codes
    assert "1d" in codes

def test_clear_cache(client):
    """Test cache clearing endpoint"""
    
    response = client.post("/api/market-data/cache/clear")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "message" in data
    assert "timestamp" in data
    assert "all symbols" in data["message"]

def test_clear_cache_specific_symbol(client):
    """Test cache clearing for specific symbol"""
    
    response = client.post("/api/market-data/cache/clear?symbol=000001")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "000001" in data["message"]

def test_health_check_endpoint(setup_test_db, client):
    """Test market data health check endpoint"""
    
    with patch('backend.app.api.market_data.market_data_provider') as mock_provider, \
         patch('backend.app.api.market_data.data_cache_service') as mock_cache:
        
        mock_provider.is_connected = True
        mock_cache.get_kline_data = AsyncMock(return_value=[{"test": "data"}])
        
        response = client.get("/api/market-data/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["market_data_connected"] == True
        assert data["data_available"] == True
        assert "timestamp" in data

def test_health_check_degraded(setup_test_db, client):
    """Test health check when service is degraded"""
    
    with patch('backend.app.api.market_data.market_data_provider') as mock_provider:
        mock_provider.is_connected = False
        
        response = client.get("/api/market-data/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "degraded"
        assert data["market_data_connected"] == False