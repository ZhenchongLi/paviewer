from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from backend.app.database import get_db_session
from backend.app.models.market_data import KLineData, RealtimeData
from backend.app.services.market_data import market_data_provider

class DataCacheService:
    """Service for caching and retrieving market data"""
    
    def __init__(self):
        self.cache_duration = {
            "1m": timedelta(hours=1),
            "5m": timedelta(hours=6), 
            "15m": timedelta(days=1),
            "1h": timedelta(days=7),
            "1d": timedelta(days=30)
        }
    
    async def get_kline_data(
        self, 
        symbol: str, 
        timeframe: str, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """Get K-line data with caching"""
        
        if use_cache:
            # Try to get data from cache first
            cached_data = self._get_cached_kline_data(symbol, timeframe, start_time, end_time)
            
            # Check if we have sufficient cached data
            if self._is_cache_sufficient(cached_data, start_time, end_time, timeframe):
                return [item.to_dict() for item in cached_data]
        
        # Fetch fresh data from market data provider
        fresh_data = await market_data_provider.get_kline_data(
            symbol, timeframe, start_time, end_time
        )
        
        # Cache the fresh data
        if fresh_data:
            await self._cache_kline_data(symbol, timeframe, fresh_data)
        
        return fresh_data
    
    def _get_cached_kline_data(
        self,
        symbol: str,
        timeframe: str, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[KLineData]:
        """Retrieve cached K-line data from database"""
        
        with get_db_session() as session:
            query = session.query(KLineData).filter(
                and_(
                    KLineData.symbol == symbol,
                    KLineData.timeframe == timeframe
                )
            )
            
            if start_time:
                query = query.filter(KLineData.timestamp >= start_time)
            if end_time:
                query = query.filter(KLineData.timestamp <= end_time)
            
            return query.order_by(KLineData.timestamp.asc()).all()
    
    def _is_cache_sufficient(
        self,
        cached_data: List[KLineData],
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        timeframe: str
    ) -> bool:
        """Check if cached data is sufficient and not stale"""
        
        if not cached_data:
            return False
        
        # Check if cache is not too old
        cache_max_age = self.cache_duration.get(timeframe, timedelta(hours=1))
        now = datetime.now()
        
        # Use created_at if available, otherwise use a recent timestamp
        try:
            latest_cached = max(item.created_at for item in cached_data if item.created_at)
        except (ValueError, AttributeError):
            # If no created_at, assume data is recent
            return True
        
        if now - latest_cached > cache_max_age:
            return False
        
        # Check if we have the requested time range
        if start_time and cached_data[0].timestamp > start_time:
            return False
        if end_time and cached_data[-1].timestamp < end_time:
            return False
        
        return True
    
    async def _cache_kline_data(
        self, 
        symbol: str, 
        timeframe: str, 
        data: List[Dict[str, Any]]
    ) -> None:
        """Cache K-line data to database"""
        
        if not data:
            return
        
        with get_db_session() as session:
            # Clear old data for this symbol/timeframe to avoid duplicates
            session.query(KLineData).filter(
                and_(
                    KLineData.symbol == symbol,
                    KLineData.timeframe == timeframe
                )
            ).delete()
            
            # Insert new data
            for item in data:
                kline = KLineData.from_market_data(symbol, timeframe, item)
                session.add(kline)
    
    async def cache_realtime_data(self, data: Dict[str, Any]) -> None:
        """Cache real-time tick data"""
        
        with get_db_session() as session:
            realtime = RealtimeData.from_tick_data(data)
            session.add(realtime)
            
            # Clean up old real-time data (keep only last 1000 records per symbol)
            old_data = session.query(RealtimeData).filter(
                RealtimeData.symbol == data["symbol"]
            ).order_by(desc(RealtimeData.timestamp)).offset(1000).all()
            
            for item in old_data:
                session.delete(item)
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get the latest cached price for a symbol"""
        
        with get_db_session() as session:
            # Try real-time data first
            latest_realtime = session.query(RealtimeData).filter(
                RealtimeData.symbol == symbol
            ).order_by(desc(RealtimeData.timestamp)).first()
            
            if latest_realtime:
                return latest_realtime.price
            
            # Fall back to latest K-line close price
            latest_kline = session.query(KLineData).filter(
                KLineData.symbol == symbol
            ).order_by(desc(KLineData.timestamp)).first()
            
            if latest_kline:
                return latest_kline.close_price
            
            return None
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> None:
        """Clean up old cached data"""
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        with get_db_session() as session:
            # Clean up old K-line data
            session.query(KLineData).filter(
                KLineData.timestamp < cutoff_date
            ).delete()
            
            # Clean up old real-time data
            session.query(RealtimeData).filter(
                RealtimeData.timestamp < cutoff_date
            ).delete()

# Global instance
data_cache_service = DataCacheService()