"""
Test error handling and structured error responses.

This test ensures that ALL API errors return structured JSON with:
- success: false
- status: HTTP status code
- error: { message, type, source }
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

# Create test client
client = TestClient(app, base_url="http://test")


def test_validation_error_returns_structured_json():
    """Test that validation errors return structured JSON."""
    # Invalid date format
    response = client.get("/api/v1/kundli?dob=invalid&time=18:38&lat=12.9716&lon=77.5946&timezone=Asia/Kolkata")
    
    assert response.status_code != 200
    assert response.status_code in [400, 422, 500]
    
    data = response.json()
    
    # Must have structured error format
    assert "success" in data
    assert data["success"] is False
    assert "status" in data
    assert data["status"] == response.status_code
    assert "error" in data
    assert "message" in data["error"]
    assert "type" in data["error"]
    assert "source" in data["error"]
    assert data["error"]["source"] == "guru-api"
    
    # Message must be non-empty
    assert data["error"]["message"]
    assert data["error"]["message"] != "{}"
    assert len(data["error"]["message"]) > 0


def test_404_returns_structured_json():
    """Test that 404 errors return structured JSON."""
    response = client.get("/api/v1/nonexistent-endpoint")
    
    assert response.status_code == 404
    
    data = response.json()
    
    # Must have structured error format
    assert "success" in data
    assert data["success"] is False
    assert "status" in data
    assert data["status"] == 404
    assert "error" in data
    assert "message" in data["error"]
    assert "type" in data["error"]
    assert "source" in data["error"]
    
    # Message must be non-empty
    assert data["error"]["message"]
    assert data["error"]["message"] != "{}"


def test_missing_required_params_returns_structured_json():
    """Test that missing required parameters return structured JSON."""
    # Missing required parameters
    response = client.get("/api/v1/kundli")
    
    assert response.status_code != 200
    assert response.status_code in [400, 422, 500]
    
    data = response.json()
    
    # Must have structured error format
    assert "success" in data
    assert data["success"] is False
    assert "status" in data
    assert "error" in data
    assert "message" in data["error"]
    
    # Message must be non-empty
    assert data["error"]["message"]
    assert data["error"]["message"] != "{}"
    assert len(data["error"]["message"]) > 0


def test_invalid_birth_details_returns_structured_json():
    """Test that invalid birth details return structured JSON."""
    # Invalid coordinates (out of range)
    response = client.get(
        "/api/v1/kundli?dob=1995-05-16&time=18:38&lat=999&lon=999&timezone=Asia/Kolkata"
    )
    
    # May return 200 (if validation passes) or error
    if response.status_code != 200:
        data = response.json()
        
        # Must have structured error format
        assert "success" in data
        assert data["success"] is False
        assert "status" in data
        assert "error" in data
        assert "message" in data["error"]
        
        # Message must be non-empty
        assert data["error"]["message"]
        assert data["error"]["message"] != "{}"


def test_error_message_is_never_empty():
    """Regression test: Ensure error message is NEVER empty or '{}'."""
    # Test various error scenarios
    test_cases = [
        ("/api/v1/kundli", "GET"),  # Missing params
        ("/api/v1/kundli?dob=invalid", "GET"),  # Invalid date
        ("/api/v1/nonexistent", "GET"),  # 404
    ]
    
    for endpoint, method in test_cases:
        if method == "GET":
            response = client.get(endpoint)
        else:
            response = client.post(endpoint, json={})
        
        if response.status_code != 200:
            data = response.json()
            
            # Critical: error.message must NEVER be empty
            assert "error" in data
            assert "message" in data["error"]
            message = data["error"]["message"]
            
            assert message is not None
            assert message != ""
            assert message != "{}"
            assert len(str(message)) > 0, f"Empty error message for {endpoint}"

