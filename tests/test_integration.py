"""
Integration tests for Apex Orchestrator
"""

import pytest
import time
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import sys
import pathlib

# Add src to path
src_dir = pathlib.Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from main import APP, sign


class TestIntegration:
    """Integration test suite"""
    
    def setup_method(self):
        """Set up test client and mock configuration"""
        self.client = TestClient(APP)
        self.test_key = "test_shared_key_minimum_32_chars_long"
    
    def generate_auth_headers(self, body: str):
        """Generate authentication headers"""
        timestamp = str(int(time.time()))
        signature = sign(body.encode(), timestamp)
        return {
            "X-TS": timestamp,
            "X-SIG": signature
        }
    
    @patch('main.SHARED_KEY', 'test_shared_key_minimum_32_chars_long')
    def test_health_endpoint_comprehensive(self):
        """Test comprehensive health check"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        
        assert data["ok"] is True
        assert data["service"] == "Apex Orchestrator"
        assert "version" in data
        assert "timestamp" in data
        assert "checks" in data
        
        # Verify checks are present
        assert "work_dir" in data["checks"]
        assert "log_dir" in data["checks"]
    
    @patch('main.SHARED_KEY', 'test_shared_key_minimum_32_chars_long')
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        response = self.client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        
        assert "service" in data
        assert "version" in data
        assert "uptime_seconds" in data
        assert "logs" in data
        assert "work_dir" in data
    
    @patch('main.SHARED_KEY', 'test_shared_key_minimum_32_chars_long')
    @patch('main.make_plan')
    @patch('main.run_step')
    @patch('main.notify')
    async def test_nlm_run_flow(self, mock_notify, mock_run_step, mock_make_plan):
        """Test natural language run endpoint flow"""
        from main import Plan, ToolCall
        
        # Mock the LLM response
        mock_plan = Plan(
            intent="Test automation",
            steps=[
                ToolCall(tool="shell", args={"cmd": "dir"}, description="List directory")
            ]
        )
        mock_make_plan.return_value = mock_plan
        
        # Mock step execution
        mock_run_step.return_value = {"returncode": 0, "stdout": "test output"}
        
        # Mock notify to be async
        mock_notify.return_value = AsyncMock()
        
        # Prepare request
        body = '{"text": "list files in directory"}'
        headers = self.generate_auth_headers(body)
        
        # Execute request
        response = self.client.post("/nlm/run", content=body, headers=headers)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "run_id" in data
        assert "plan" in data
    
    @patch('main.SHARED_KEY', 'test_shared_key_minimum_32_chars_long')
    @patch('main.run_step')
    def test_direct_operation(self, mock_run_step):
        """Test direct operation endpoint"""
        # Mock step execution
        mock_run_step.return_value = {"status": "success"}
        
        # Prepare request
        body = '{"op": "shell", "params": {"cmd": "dir"}}'
        headers = self.generate_auth_headers(body)
        
        # Execute request
        response = self.client.post("/apex/run", content=body, headers=headers)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "run_id" in data
    
    @patch('main.SHARED_KEY', 'test_shared_key_minimum_32_chars_long')
    def test_invalid_operation(self):
        """Test invalid operation rejection"""
        body = '{"op": "invalid_op", "params": {}}'
        headers = self.generate_auth_headers(body)
        
        response = self.client.post("/apex/run", content=body, headers=headers)
        assert response.status_code == 422  # Validation error
    
    @patch('main.SHARED_KEY', 'test_shared_key_minimum_32_chars_long')
    def test_authentication_required(self):
        """Test that authentication is required"""
        response = self.client.post("/nlm/run", json={"text": "test"})
        assert response.status_code == 401
    
    @patch('main.SHARED_KEY', 'test_shared_key_minimum_32_chars_long')
    def test_stale_timestamp_rejected(self):
        """Test that old timestamps are rejected"""
        body = '{"text": "test request"}'
        old_timestamp = str(int(time.time()) - 400)  # 400 seconds ago
        signature = sign(body.encode(), old_timestamp)
        
        headers = {
            "X-TS": old_timestamp,
            "X-SIG": signature
        }
        
        response = self.client.post("/nlm/run", content=body, headers=headers)
        assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

