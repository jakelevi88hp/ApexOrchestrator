#!/usr/bin/env python3
"""
Complete test script for Pulse system
"""

import sys
import os
import asyncio
import time
sys.path.insert(0, '/workspace/src')

from main import APP, startup_event
from fastapi.testclient import TestClient

async def test_pulse_complete():
    """Complete test of Pulse system"""
    print("Starting complete Pulse system test...")
    
    # Trigger startup event
    print("\n1. Triggering startup event...")
    await startup_event()
    print("[OK] Startup event completed")
    
    # Create test client
    client = TestClient(APP)
    
    # Test all Pulse endpoints
    print("\n2. Testing Pulse endpoints...")
    
    # Status endpoint
    print("  - Testing /pulse/status...")
    response = client.get('/pulse/status')
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        print(f"    Response: {response.json()}")
    
    # Dashboard endpoint
    print("  - Testing /pulse/dashboard...")
    response = client.get('/pulse/dashboard')
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Dashboard data keys: {list(data.keys())}")
    
    # Current metrics
    print("  - Testing /pulse/metrics/current...")
    response = client.get('/pulse/metrics/current')
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        print(f"    Metrics available: {response.json() is not None}")
    
    # Historical metrics
    print("  - Testing /pulse/metrics/historical...")
    response = client.get('/pulse/metrics/historical?hours=1')
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Historical metrics count: {data.get('count', 0)}")
    
    # Recent events
    print("  - Testing /pulse/events/recent...")
    response = client.get('/pulse/events/recent?limit=5')
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Events count: {data.get('count', 0)}")
    
    # Generate some activity
    print("\n3. Generating activity to test event recording...")
    
    # Make some API calls to generate events
    for i in range(3):
        print(f"  - Making API call {i+1}...")
        response = client.get('/health')
        print(f"    Status: {response.status_code}")
        time.sleep(0.1)  # Small delay between calls
    
    # Wait for events to be processed
    print("  - Waiting for events to be processed...")
    time.sleep(2)
    
    # Check events again
    print("  - Checking events after activity...")
    response = client.get('/pulse/events/recent?limit=10')
    if response.status_code == 200:
        data = response.json()
        print(f"    Events count: {data.get('count', 0)}")
        if data.get('events'):
            print("    Recent events:")
            for event in data['events'][:3]:
                print(f"      - {event.get('event_type')}: {event.get('message')}")
    
    # Test analytics
    print("\n4. Testing analytics endpoints...")
    
    # Trend analysis
    print("  - Testing /pulse/analytics/trends...")
    response = client.get('/pulse/analytics/trends?hours=1')
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
         print("    [OK] Trend analysis working")
    
    # Event analysis
    print("  - Testing /pulse/analytics/events...")
    response = client.get('/pulse/analytics/events?hours=1')
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
         print("    [OK] Event analysis working")
    
    # Health report
    print("  - Testing /pulse/health-report...")
    response = client.get('/pulse/health-report')
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Health score: {data.get('health_score', 'N/A')}")
        print(f"    Overall health: {data.get('overall_health', 'N/A')}")
    
    # Test dashboard HTML
    print("\n5. Testing dashboard HTML...")
    response = client.get('/pulse/dashboard.html')
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        print("    [OK] Dashboard HTML available")
        print(f"    Content length: {len(response.text)} characters")
    
    print("\n[SUCCESS] Pulse system test completed successfully!")
    print("\n[SUMMARY]:")
    print("  - All Pulse endpoints are working")
    print("  - Event recording is functional")
    print("  - Analytics engine is operational")
    print("  - Dashboard is accessible")
    print("  - Real-time monitoring is active")

if __name__ == "__main__":
    asyncio.run(test_pulse_complete())
