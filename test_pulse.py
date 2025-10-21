#!/usr/bin/env python3
"""
Test script for Pulse system
"""

import sys
import os
sys.path.insert(0, '/workspace/src')

from main import APP
from fastapi.testclient import TestClient
import time

def test_pulse_system():
    """Test the Pulse system functionality"""
    print("Testing Pulse system...")
    
    # Create test client
    client = TestClient(APP)
    
    # Test Pulse status endpoint
    print("\n1. Testing Pulse status endpoint...")
    response = client.get('/pulse/status')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    
    # Test Pulse dashboard endpoint
    print("\n2. Testing Pulse dashboard endpoint...")
    response = client.get('/pulse/dashboard')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Dashboard data keys: {list(data.keys())}")
    else:
        print(f"Error: {response.text}")
    
    # Test Pulse metrics endpoint
    print("\n3. Testing Pulse metrics endpoint...")
    response = client.get('/pulse/metrics/current')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    
    # Test Pulse events endpoint
    print("\n4. Testing Pulse events endpoint...")
    response = client.get('/pulse/events/recent?limit=5')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")
    
    # Test health endpoint to generate some events
    print("\n5. Testing health endpoint to generate events...")
    response = client.get('/health')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("Health check successful - should have generated pulse events")
    
    # Wait a moment for events to be processed
    time.sleep(1)
    
    # Test events again to see if new events were recorded
    print("\n6. Testing events after health check...")
    response = client.get('/pulse/events/recent?limit=5')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        events = response.json()
        print(f"Events count: {events.get('count', 0)}")
        if events.get('events'):
            print("Recent events:")
            for event in events['events'][:3]:
                print(f"  - {event.get('event_type')}: {event.get('message')}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_pulse_system()
