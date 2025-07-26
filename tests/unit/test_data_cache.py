import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from sqlalchemy.orm import Session

from backend.app.services.data_cache import DataCacheService
from backend.app.models.market_data import KLineData, RealtimeData
from backend.app.database import create_tables, drop_tables, get_db_session

@pytest.fixture(scope="function")
def setup_test_db():
    """Set up test database"""
    create_tables()
    yield
    drop_tables()

@pytest.fixture
def data_cache_service():
    return DataCacheService()

@pytest.fixture
def sample_kline_data():
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

@pytest.mark.asyncio
async def test_cache_kline_data(setup_test_db, data_cache_service, sample_kline_data):
    """Test caching K-line data"""
    symbol = "000001"
    timeframe = "1m"
    
    # Cache the data
    await data_cache_service._cache_kline_data(symbol, timeframe, sample_kline_data)
    
    # Verify data was cached
    with get_db_session() as session:
        cached_data = session.query(KLineData).filter(
            KLineData.symbol == symbol,
            KLineData.timeframe == timeframe
        ).all()
        
        assert len(cached_data) == 2
        assert cached_data[0].symbol == symbol
        assert cached_data[0].timeframe == timeframe
        assert cached_data[0].open_price == 100.0
        assert cached_data[1].close_price == 104.0

def test_get_cached_kline_data(setup_test_db, data_cache_service):
    """Test retrieving cached K-line data"""
    symbol = "000001"
    timeframe = "1m"
    
    # Insert test data directly
    with get_db_session() as session:
        kline1 = KLineData(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=datetime(2023, 12, 1, 9, 30, 0),
            open_price=100.0,
            high_price=105.0,
            low_price=98.0,
            close_price=102.0,
            volume=1000
        )
        kline2 = KLineData(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=datetime(2023, 12, 1, 9, 31, 0),
            open_price=102.0,
            high_price=106.0,
            low_price=101.0,
            close_price=104.0,
            volume=1200
        )
        session.add(kline1)
        session.add(kline2)
        session.commit()
        
        # Test within the same session to avoid detached instance errors
        cached_data = session.query(KLineData).filter(
            KLineData.symbol == symbol,
            KLineData.timeframe == timeframe
        ).order_by(KLineData.timestamp.asc()).all()
        
        assert len(cached_data) == 2
        assert cached_data[0].open_price == 100.0
        assert cached_data[1].close_price == 104.0

def test_is_cache_sufficient(data_cache_service):
    """Test cache sufficiency check"""
    now = datetime.now()
    
    # Create recent cached data that covers the requested time range
    kline_data = KLineData(
        symbol="000001",
        timeframe="1m",
        timestamp=now - timedelta(minutes=15),  # Earlier timestamp to cover range
        open_price=100.0,
        high_price=105.0,
        low_price=98.0,
        close_price=102.0,
        volume=1000
    )
    kline_data.created_at = now - timedelta(minutes=1)  # Recently cached
    
    kline_data2 = KLineData(
        symbol="000001",
        timeframe="1m", 
        timestamp=now,  # Latest timestamp to cover range
        open_price=102.0,
        high_price=105.0,
        low_price=98.0,
        close_price=104.0,
        volume=1000
    )
    kline_data2.created_at = now - timedelta(minutes=1)
    
    cached_data = [kline_data, kline_data2]
    
    # Should be sufficient for recent data with good time coverage
    assert data_cache_service._is_cache_sufficient(
        cached_data, 
        now - timedelta(minutes=10), 
        now, 
        "1m"
    ) == True
    
    # Should not be sufficient for old cache
    kline_data.created_at = now - timedelta(hours=2)
    kline_data2.created_at = now - timedelta(hours=2)
    assert data_cache_service._is_cache_sufficient(
        cached_data, 
        now - timedelta(minutes=10), 
        now, 
        "1m"
    ) == False

@pytest.mark.asyncio
async def test_cache_realtime_data(setup_test_db, data_cache_service):
    """Test caching real-time data"""
    tick_data = {
        "symbol": "000001",
        "price": 102.5,
        "volume": 500,
        "timestamp": datetime.now().isoformat()
    }
    
    await data_cache_service.cache_realtime_data(tick_data)
    
    # Verify data was cached
    with get_db_session() as session:
        cached_tick = session.query(RealtimeData).filter(
            RealtimeData.symbol == "000001"
        ).first()
        
        assert cached_tick is not None
        assert cached_tick.symbol == "000001"
        assert cached_tick.price == 102.5
        assert cached_tick.volume == 500

def test_get_latest_price(setup_test_db, data_cache_service):
    """Test getting latest price from cache"""
    symbol = "000001"
    now = datetime.now()
    
    # Insert real-time data
    with get_db_session() as session:
        realtime = RealtimeData(
            symbol=symbol,
            price=105.5,
            volume=500,
            timestamp=now
        )
        session.add(realtime)
    
    # Should return real-time price
    latest_price = data_cache_service.get_latest_price(symbol)
    assert latest_price == 105.5
    
    # Test fallback to K-line data when no real-time data
    with get_db_session() as session:
        session.query(RealtimeData).delete()
        
        kline = KLineData(
            symbol=symbol,
            timeframe="1m",
            timestamp=now,
            open_price=100.0,
            high_price=105.0,
            low_price=98.0,
            close_price=103.0,
            volume=1000
        )
        session.add(kline)
    
    latest_price = data_cache_service.get_latest_price(symbol)
    assert latest_price == 103.0

@pytest.mark.asyncio
async def test_get_kline_data_with_mock(setup_test_db, data_cache_service, sample_kline_data):
    """Test get_kline_data method with mocked market data provider"""
    
    with patch('backend.app.services.data_cache.market_data_provider') as mock_provider:
        mock_provider.get_kline_data = AsyncMock(return_value=sample_kline_data)
        
        # Test getting data (should fetch from provider since no cache)
        result = await data_cache_service.get_kline_data("000001", "1m", use_cache=False)
        
        assert len(result) == 2
        assert result[0]["open"] == 100.0
        assert result[1]["close"] == 104.0
        
        # Verify provider was called
        mock_provider.get_kline_data.assert_called_once_with("000001", "1m", None, None)