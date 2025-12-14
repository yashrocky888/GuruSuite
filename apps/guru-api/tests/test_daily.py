"""
Tests for Daily prediction calculations.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_get_daily_prediction():
    """Test complete daily prediction."""
    request_data = {
        "birth_date": "1990-01-01T12:00:00",
        "birth_time": "10:30",
        "birth_latitude": 28.6139,
        "birth_longitude": 77.2090,
        "timezone": "Asia/Kolkata"
    }
    
    response = client.post("/api/v1/daily", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "daily_rating" in data
    assert "lucky_color" in data
    assert "best_times" in data
    assert "summary" in data
    assert "rating" in data["daily_rating"]
    assert "primary_color" in data["lucky_color"]


def test_get_daily_rating():
    """Test getting only daily rating."""
    request_data = {
        "birth_date": "1990-01-01T12:00:00",
        "birth_time": "10:30",
        "birth_latitude": 28.6139,
        "birth_longitude": 77.2090,
        "timezone": "Asia/Kolkata"
    }
    
    response = client.post("/api/v1/daily/rating", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "rating" in data
    assert "score" in data
    assert "factors" in data
    assert data["rating"] in ["Excellent", "Good", "Mixed", "Caution"]


def test_get_lucky_color():
    """Test getting lucky color."""
    request_data = {
        "birth_date": "1990-01-01T12:00:00",
        "birth_time": "10:30",
        "birth_latitude": 28.6139,
        "birth_longitude": 77.2090,
        "timezone": "Asia/Kolkata"
    }
    
    response = client.post("/api/v1/daily/color", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "primary_color" in data
    assert "all_colors" in data
    assert "based_on" in data

