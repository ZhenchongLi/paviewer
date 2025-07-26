import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_kline_data():
    return [
        {
            "time": "2023-12-01",
            "open": 100.0,
            "high": 110.0,
            "low": 95.0,
            "close": 105.0,
            "volume": 1000
        },
        {
            "time": "2023-12-02", 
            "open": 105.0,
            "high": 115.0,
            "low": 100.0,
            "close": 108.0,
            "volume": 1200
        }
    ]