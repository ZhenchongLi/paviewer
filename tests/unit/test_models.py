import pytest
from datetime import datetime
from backend.app.models.market_data import KLineData, RealtimeData

def test_kline_data_creation():
    """Test KLineData model creation and basic functionality"""
    kline = KLineData(
        symbol="000001",
        timeframe="1m",
        timestamp=datetime(2023, 12, 1, 9, 30, 0),
        open_price=100.0,
        high_price=105.0,
        low_price=98.0,
        close_price=102.0,
        volume=1000
    )
    
    assert kline.symbol == "000001"
    assert kline.timeframe == "1m"
    assert kline.open_price == 100.0
    assert kline.high_price == 105.0
    assert kline.low_price == 98.0
    assert kline.close_price == 102.0
    assert kline.volume == 1000

def test_kline_data_to_dict():
    """Test KLineData to_dict method"""
    timestamp = datetime(2023, 12, 1, 9, 30, 0)
    kline = KLineData(
        id=1,
        symbol="000001",
        timeframe="1m",
        timestamp=timestamp,
        open_price=100.0,
        high_price=105.0,
        low_price=98.0,
        close_price=102.0,
        volume=1000
    )
    
    result = kline.to_dict()
    
    assert result["id"] == 1
    assert result["symbol"] == "000001"
    assert result["timeframe"] == "1m"
    assert result["time"] == timestamp.isoformat()
    assert result["open"] == 100.0
    assert result["high"] == 105.0
    assert result["low"] == 98.0
    assert result["close"] == 102.0
    assert result["volume"] == 1000

def test_kline_data_from_market_data():
    """Test KLineData.from_market_data class method"""
    market_data = {
        "time": "2023-12-01T09:30:00",
        "open": 100.0,
        "high": 105.0,
        "low": 98.0,
        "close": 102.0,
        "volume": 1000
    }
    
    kline = KLineData.from_market_data("000001", "1m", market_data)
    
    assert kline.symbol == "000001"
    assert kline.timeframe == "1m"
    assert kline.timestamp == datetime(2023, 12, 1, 9, 30, 0)
    assert kline.open_price == 100.0
    assert kline.high_price == 105.0
    assert kline.low_price == 98.0
    assert kline.close_price == 102.0
    assert kline.volume == 1000

def test_realtime_data_creation():
    """Test RealtimeData model creation and basic functionality"""
    realtime = RealtimeData(
        symbol="000001",
        price=102.5,
        volume=500,
        timestamp=datetime(2023, 12, 1, 9, 30, 15)
    )
    
    assert realtime.symbol == "000001"
    assert realtime.price == 102.5
    assert realtime.volume == 500
    assert realtime.timestamp == datetime(2023, 12, 1, 9, 30, 15)

def test_realtime_data_to_dict():
    """Test RealtimeData to_dict method"""
    timestamp = datetime(2023, 12, 1, 9, 30, 15)
    realtime = RealtimeData(
        id=1,
        symbol="000001",
        price=102.5,
        volume=500,
        timestamp=timestamp
    )
    
    result = realtime.to_dict()
    
    assert result["id"] == 1
    assert result["symbol"] == "000001"
    assert result["price"] == 102.5
    assert result["volume"] == 500
    assert result["timestamp"] == timestamp.isoformat()

def test_realtime_data_from_tick_data():
    """Test RealtimeData.from_tick_data class method"""
    tick_data = {
        "symbol": "000001",
        "price": 102.5,
        "volume": 500,
        "timestamp": "2023-12-01T09:30:15"
    }
    
    realtime = RealtimeData.from_tick_data(tick_data)
    
    assert realtime.symbol == "000001"
    assert realtime.price == 102.5
    assert realtime.volume == 500
    assert realtime.timestamp == datetime(2023, 12, 1, 9, 30, 15)

def test_kline_data_validation():
    """Test KLineData with invalid data should handle type conversion"""
    market_data = {
        "time": "2023-12-01T09:30:00",
        "open": "100.0",  # String instead of float
        "high": "105.0",
        "low": "98.0", 
        "close": "102.0",
        "volume": "1000"  # String instead of int
    }
    
    kline = KLineData.from_market_data("000001", "1m", market_data)
    
    # Should convert strings to proper types
    assert isinstance(kline.open_price, float)
    assert isinstance(kline.volume, int)
    assert kline.open_price == 100.0
    assert kline.volume == 1000