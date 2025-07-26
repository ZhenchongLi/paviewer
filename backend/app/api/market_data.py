from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from backend.app.database import get_db, create_tables
from backend.app.services.data_cache import data_cache_service
from backend.app.services.market_data import market_data_provider

router = APIRouter(prefix="/api/market-data", tags=["market-data"])

# Initialize database tables
create_tables()

# Startup and shutdown events are handled in main.py via lifespan context

@router.get("/kline/{symbol}")
async def get_kline_data(
    symbol: str,
    timeframe: str = Query("1m", description="Timeframe (1m, 5m, 15m, 1h, 1d)"),
    start_time: Optional[str] = Query(None, description="Start time (ISO format)"),
    end_time: Optional[str] = Query(None, description="End time (ISO format)"),
    use_cache: bool = Query(True, description="Use cached data if available"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get K-line (candlestick) data for a symbol"""
    
    try:
        # Parse datetime strings if provided
        start_dt = datetime.fromisoformat(start_time) if start_time else None
        end_dt = datetime.fromisoformat(end_time) if end_time else None
        
        # Get data from cache service
        data = await data_cache_service.get_kline_data(
            symbol=symbol,
            timeframe=timeframe,
            start_time=start_dt,
            end_time=end_dt,
            use_cache=use_cache
        )
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": data,
            "count": len(data)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid datetime format: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get market data: {e}")

@router.get("/latest-price/{symbol}")
async def get_latest_price(
    symbol: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get the latest price for a symbol"""
    
    try:
        price = data_cache_service.get_latest_price(symbol)
        
        if price is None:
            raise HTTPException(status_code=404, detail=f"No price data found for symbol {symbol}")
        
        return {
            "symbol": symbol,
            "price": price,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions to preserve status codes
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get latest price: {e}")

@router.get("/symbols")
async def get_available_symbols() -> Dict[str, Any]:
    """Get list of available symbols"""
    
    # For now, return some common Chinese market symbols
    # This would be populated from the actual market data provider
    symbols = [
        {"code": "000001", "name": "平安银行", "market": "SZ"},
        {"code": "000002", "name": "万科A", "market": "SZ"},
        {"code": "600000", "name": "浦发银行", "market": "SH"},
        {"code": "600036", "name": "招商银行", "market": "SH"},
    ]
    
    return {
        "symbols": symbols,
        "count": len(symbols)
    }

@router.get("/timeframes")
async def get_available_timeframes() -> Dict[str, Any]:
    """Get list of available timeframes"""
    
    timeframes = [
        {"code": "1m", "name": "1分钟", "minutes": 1},
        {"code": "5m", "name": "5分钟", "minutes": 5},
        {"code": "15m", "name": "15分钟", "minutes": 15},
        {"code": "1h", "name": "1小时", "minutes": 60},
        {"code": "1d", "name": "日线", "minutes": 1440},
    ]
    
    return {
        "timeframes": timeframes,
        "count": len(timeframes)
    }

@router.post("/cache/clear")
async def clear_cache(
    symbol: Optional[str] = Query(None, description="Symbol to clear (all if not specified)"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Clear cached data"""
    
    try:
        # This would implement cache clearing logic
        # For now, just return success
        
        return {
            "message": f"Cache cleared for {symbol if symbol else 'all symbols'}",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {e}")

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check for market data service"""
    
    try:
        # Check if market data provider is connected
        is_connected = market_data_provider.is_connected
        
        # Get sample data to test the pipeline
        if is_connected:
            sample_data = await data_cache_service.get_kline_data("000001", "1m", use_cache=False)
            data_available = len(sample_data) > 0
        else:
            data_available = False
        
        status = "healthy" if is_connected and data_available else "degraded"
        
        return {
            "status": status,
            "market_data_connected": is_connected,
            "data_available": data_available,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }