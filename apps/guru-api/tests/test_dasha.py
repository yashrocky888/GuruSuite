"""
Tests for Dasha (Planetary Periods) calculations.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_calculate_dasha():
    """Test dasha calculation."""
    request_data = {
        "birth_date": "1990-01-01T12:00:00",
        "birth_time": "10:30",
        "birth_latitude": 28.6139,
        "birth_longitude": 77.2090,
        "timezone": "Asia/Kolkata"
    }
    
    response = client.post("/api/v1/dasha", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "current_dasha" in data
    assert "current_antardasha" in data
    assert "dasha_sequence" in data
    assert "lord" in data["current_dasha"]


def test_get_current_dasha():
    """Test getting only current dasha."""
    request_data = {
        "birth_date": "1990-01-01T12:00:00",
        "birth_time": "10:30",
        "birth_latitude": 28.6139,
        "birth_longitude": 77.2090,
        "timezone": "Asia/Kolkata"
    }
    
    response = client.post("/api/v1/dasha/current", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "current_dasha" in data
    assert "current_antardasha" in data
    assert "upcoming_antardashas" in data

