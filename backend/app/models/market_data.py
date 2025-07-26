from sqlalchemy import Column, Integer, Float, String, DateTime, BigInteger, Index
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any

Base = declarative_base()

class KLineData(Base):
    """K-line (candlestick) data model"""
    __tablename__ = "kline_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)  # 1m, 5m, 15m, 1h, 1d
    timestamp = Column(DateTime, nullable=False)
    
    # OHLCV data
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_symbol_timeframe_timestamp', 'symbol', 'timeframe', 'timestamp'),
        Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "time": self.timestamp.isoformat() if self.timestamp else None,
            "open": self.open_price,
            "high": self.high_price,
            "low": self.low_price,
            "close": self.close_price,
            "volume": self.volume
        }
    
    @classmethod
    def from_market_data(cls, symbol: str, timeframe: str, data: Dict[str, Any]) -> 'KLineData':
        """Create KLineData instance from market data dictionary"""
        return cls(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=datetime.fromisoformat(data["time"]) if isinstance(data["time"], str) else data["time"],
            open_price=float(data["open"]),
            high_price=float(data["high"]),
            low_price=float(data["low"]),
            close_price=float(data["close"]),
            volume=int(data["volume"])
        )
    
    def __repr__(self):
        return f"<KLineData({self.symbol}, {self.timeframe}, {self.timestamp}, O:{self.open_price}, H:{self.high_price}, L:{self.low_price}, C:{self.close_price})>"

class RealtimeData(Base):
    """Real-time tick data model"""
    __tablename__ = "realtime_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    price = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    
    # Index for efficient queries
    __table_args__ = (
        Index('idx_symbol_timestamp_rt', 'symbol', 'timestamp'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "price": self.price,
            "volume": self.volume,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_tick_data(cls, data: Dict[str, Any]) -> 'RealtimeData':
        """Create RealtimeData instance from tick data dictionary"""
        return cls(
            symbol=data["symbol"],
            price=float(data["price"]),
            volume=int(data["volume"]),
            timestamp=datetime.fromisoformat(data["timestamp"]) if isinstance(data["timestamp"], str) else data["timestamp"]
        )
    
    def __repr__(self):
        return f"<RealtimeData({self.symbol}, P:{self.price}, V:{self.volume}, {self.timestamp})>"