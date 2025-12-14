"""
Tests for Kundli (Birth Chart) calculations.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_calculate_kundli():
    """Test basic kundli calculation."""
    request_data = {
        "name": "Test User",
        "birth_date": "1990-01-01T12:00:00",
        "birth_time": "10:30",
        "birth_latitude": 28.6139,
        "birth_longitude": 77.2090,
        "birth_place": "New Delhi",
        "timezone": "Asia/Kolkata"
    }
    
    response = client.post("/api/v1/kundli", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "name" in data
    assert "planets" in data
    assert "houses" in data
    assert "ascendant" in data
    assert data["name"] == "Test User"


def test_get_planets():
    """Test getting only planet positions."""
    request_data = {
        "name": "Test User",
        "birth_date": "1990-01-01T12:00:00",
        "birth_time": "10:30",
        "birth_latitude": 28.6139,
        "birth_longitude": 77.2090,
        "birth_place": "New Delhi",
        "timezone": "Asia/Kolkata"
    }
    
    response = client.post("/api/v1/kundli/planets", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "planets" in data
    assert "ascendant" in data
    assert "Sun" in data["planets"]
    assert "Moon" in data["planets"]


def test_get_houses():
    """Test getting only house cusps."""
    request_data = {
        "name": "Test User",
        "birth_date": "1990-01-01T12:00:00",
        "birth_time": "10:30",
        "birth_latitude": 28.6139,
        "birth_longitude": 77.2090,
        "birth_place": "New Delhi",
        "timezone": "Asia/Kolkata"
    }
    
    response = client.post("/api/v1/kundli/houses", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "houses" in data
    assert "ascendant" in data
    assert "house_1" in data["houses"]


def test_get_navamsa():
    """Test Navamsa (D9) calculation."""
    request_data = {
        "name": "Test User",
        "birth_date": "1990-01-01T12:00:00",
        "birth_time": "10:30",
        "birth_latitude": 28.6139,
        "birth_longitude": 77.2090,
        "birth_place": "New Delhi",
        "timezone": "Asia/Kolkata"
    }
    
    response = client.post("/api/v1/kundli/navamsa", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "chart_type" in data
    assert data["chart_type"] == "D9 (Navamsa)"
    assert "planets" in data


def test_get_yogas():
    """Test yogas calculation."""
    request_data = {
        "name": "Test User",
        "birth_date": "1990-01-01T12:00:00",
        "birth_time": "10:30",
        "birth_latitude": 28.6139,
        "birth_longitude": 77.2090,
        "birth_place": "New Delhi",
        "timezone": "Asia/Kolkata"
    }
    
    response = client.post("/api/v1/kundli/yogas", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "total_yogas" in data
    assert "yogas" in data
    assert "summary" in data

