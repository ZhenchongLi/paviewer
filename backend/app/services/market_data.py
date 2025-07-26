from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import random

class MarketDataProvider(ABC):
    """Abstract base class for market data providers"""
    
    @abstractmethod
    async def get_kline_data(
        self, 
        symbol: str, 
        timeframe: str, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get K-line (candlestick) data"""
        pass
    
    @abstractmethod
    async def subscribe_realtime_data(self, symbol: str, callback) -> None:
        """Subscribe to real-time market data"""
        pass

class MockMarketDataProvider(MarketDataProvider):
    """Mock implementation for development and testing"""
    
    def __init__(self):
        self.is_connected = False
        self.subscriptions = {}
    
    async def connect(self) -> bool:
        """Mock connection to market data"""
        await asyncio.sleep(0.1)  # Simulate connection delay
        self.is_connected = True
        return True
    
    async def disconnect(self) -> None:
        """Mock disconnection"""
        self.is_connected = False
        self.subscriptions.clear()
    
    async def get_kline_data(
        self, 
        symbol: str, 
        timeframe: str, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Generate mock K-line data"""
        if not self.is_connected:
            raise ConnectionError("Not connected to market data provider")
        
        # Generate sample data based on timeframe
        data_points = 100
        base_price = 100.0
        
        kline_data = []
        for i in range(data_points):
            # Simulate price movement
            open_price = base_price + random.uniform(-5, 5)
            close_price = open_price + random.uniform(-3, 3)
            high_price = max(open_price, close_price) + random.uniform(0, 2)
            low_price = min(open_price, close_price) - random.uniform(0, 2)
            volume = random.randint(1000, 10000)
            
            kline_data.append({
                "time": f"2023-12-{i+1:02d}",
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume
            })
            
            base_price = close_price
        
        return kline_data
    
    async def subscribe_realtime_data(self, symbol: str, callback) -> None:
        """Mock real-time data subscription"""
        if not self.is_connected:
            raise ConnectionError("Not connected to market data provider")
        
        self.subscriptions[symbol] = callback
        
        # Start mock data streaming
        asyncio.create_task(self._stream_mock_data(symbol, callback))
    
    async def _stream_mock_data(self, symbol: str, callback):
        """Stream mock real-time data"""
        base_price = 100.0
        
        while symbol in self.subscriptions and self.is_connected:
            # Generate real-time tick data
            price_change = random.uniform(-0.5, 0.5)
            new_price = base_price + price_change
            volume = random.randint(100, 1000)
            
            tick_data = {
                "symbol": symbol,
                "price": round(new_price, 2),
                "volume": volume,
                "timestamp": datetime.now().isoformat()
            }
            
            await callback(tick_data)
            base_price = new_price
            
            # Wait 1 second between updates
            await asyncio.sleep(1.0)

# Global instance
market_data_provider = MockMarketDataProvider()