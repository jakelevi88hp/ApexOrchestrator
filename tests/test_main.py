"""
Basic tests for Apex Orchestrator
"""

import pytest
import json
import hmac
import hashlib
import time
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys
import pathlib

# Add src to path
src_dir = pathlib.Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from main import APP, sign, verify


class TestApexOrchestrator:
    """Test suite for Apex Orchestrator"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(APP)
        self.test_key = "test_shared_key_123"
    
    def generate_auth_headers(self, body: str, timestamp: str = None):
        """Generate authentication headers for testing"""
        if timestamp is None:
            timestamp = str(int(time.time()))
        signature = sign(body.encode(), timestamp)
        return {
            "X-TS": timestamp,
            "X-SIG": signature
        }
    
    @patch('main.SHARED_KEY', 'test_shared_key_123')
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["service"] == "Apex Orchestrator"
    
    @patch('main.SHARED_KEY', 'test_shared_key_123')
    def test_auth_echo_sign(self):
        """Test signature generation endpoint"""
        test_body = '{"test": "data"}'
        response = self.client.post("/auth/echo-sign", content=test_body)
        assert response.status_code == 200
        data = response.json()
        assert "ts" in data
        assert "sig" in data
    
    @patch('main.SHARED_KEY', 'test_shared_key_123')
    def test_authentication_verification(self):
        """Test authentication verification"""
        # Test valid signature
        body = '{"test": "data"}'
        timestamp = str(int(time.time()))
        signature = sign(body.encode(), timestamp)
        
        # This should not raise an exception
        verify(signature, timestamp, body.encode())
        
        # Test invalid signature
        with pytest.raises(Exception):
            verify("invalid_signature", timestamp, body.encode())
    
    @patch('main.SHARED_KEY', 'test_shared_key_123')
    def test_missing_auth_headers(self):
        """Test requests without authentication headers"""
        body = '{"text": "test request"}'
        response = self.client.post("/nlm/run", content=body)
        assert response.status_code == 401
    
    @patch('main.SHARED_KEY', 'test_shared_key_123')
    def test_invalid_auth_headers(self):
        """Test requests with invalid authentication"""
        body = '{"text": "test request"}'
        headers = {
            "X-TS": str(int(time.time())),
            "X-SIG": "invalid_signature"
        }
        response = self.client.post("/nlm/run", content=body, headers=headers)
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__])

