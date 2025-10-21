#!/usr/bin/env python3
"""
Test script to manually trigger startup and test Pulse routes
"""

import sys
import os
import asyncio
sys.path.insert(0, '/workspace/src')

from main import APP, startup_event

async def test_with_startup():
    """Test with manual startup event"""
    print("Manually triggering startup event...")
    
    # Trigger startup event
    await startup_event()
    
    print("Startup event completed")
    
    # Check routes after startup
    routes = []
    for route in APP.routes:
        if hasattr(route, 'path'):
            routes.append(route.path)
        elif hasattr(route, 'routes'):  # For sub-routers
            for sub_route in route.routes:
                if hasattr(sub_route, 'path'):
                    routes.append(f"{route.prefix}{sub_route.path}")
    
    print(f"Total routes after startup: {len(routes)}")
    
    # Check for Pulse routes specifically
    pulse_routes = [r for r in routes if '/pulse' in r]
    print(f"Pulse routes: {len(pulse_routes)}")
    for route in pulse_routes:
        print(f"  {route}")
    
    # Test a Pulse endpoint
    from fastapi.testclient import TestClient
    client = TestClient(APP)
    
    print("\nTesting Pulse status endpoint...")
    response = client.get('/pulse/status')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_with_startup())
