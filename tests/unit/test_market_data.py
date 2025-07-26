import pytest
import asyncio
from unittest.mock import AsyncMock
from backend.app.services.market_data import MockMarketDataProvider

@pytest.mark.asyncio
async def test_mock_provider_connection():
    provider = MockMarketDataProvider()
    
    # Test initial state
    assert not provider.is_connected
    
    # Test connection
    result = await provider.connect()
    assert result is True
    assert provider.is_connected
    
    # Test disconnection
    await provider.disconnect()
    assert not provider.is_connected

@pytest.mark.asyncio
async def test_get_kline_data_requires_connection():
    provider = MockMarketDataProvider()
    
    # Test without connection
    with pytest.raises(ConnectionError):
        await provider.get_kline_data("000001", "1m")
    
    # Test with connection
    await provider.connect()
    data = await provider.get_kline_data("000001", "1m")
    
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Validate data structure
    first_item = data[0]
    assert "time" in first_item
    assert "open" in first_item
    assert "high" in first_item
    assert "low" in first_item
    assert "close" in first_item
    assert "volume" in first_item
    
    # Validate OHLC relationships
    assert first_item["high"] >= max(first_item["open"], first_item["close"])
    assert first_item["low"] <= min(first_item["open"], first_item["close"])

@pytest.mark.asyncio
async def test_realtime_subscription():
    provider = MockMarketDataProvider()
    await provider.connect()
    
    received_data = []
    
    async def mock_callback(data):
        received_data.append(data)
    
    # Subscribe to real-time data
    await provider.subscribe_realtime_data("000001", mock_callback)
    
    # Wait for some data
    await asyncio.sleep(2.1)
    
    # Check that data was received
    assert len(received_data) >= 2
    
    # Validate data structure
    tick = received_data[0]
    assert "symbol" in tick
    assert "price" in tick
    assert "volume" in tick
    assert "timestamp" in tick
    assert tick["symbol"] == "000001"
    
    await provider.disconnect()