"""
Tests for Panchang calculations.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_calculate_panchang():
    """Test panchang calculation."""
    request_data = {
        "date": "2024-01-01T12:00:00",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "timezone": "Asia/Kolkata"
    }
    
    response = client.post("/api/v1/panchang", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "tithi" in data
    assert "nakshatra" in data
    assert "yoga" in data
    assert "karana" in data
    assert "vaar" in data
    assert "name" in data["tithi"]
    assert "name" in data["nakshatra"]

