#!/usr/bin/env python3
"""
Test script to check if Pulse routes are registered
"""

import sys
import os
sys.path.insert(0, '/workspace/src')

from main import APP

def test_routes():
    """Test if Pulse routes are registered"""
    print("Checking registered routes...")
    
    # Get all routes
    routes = []
    for route in APP.routes:
        if hasattr(route, 'path'):
            routes.append(route.path)
        elif hasattr(route, 'routes'):  # For sub-routers
            for sub_route in route.routes:
                if hasattr(sub_route, 'path'):
                    routes.append(f"{route.prefix}{sub_route.path}")
    
    print(f"Total routes: {len(routes)}")
    print("\nAll routes:")
    for route in sorted(routes):
        print(f"  {route}")
    
    # Check for Pulse routes specifically
    pulse_routes = [r for r in routes if '/pulse' in r]
    print(f"\nPulse routes: {len(pulse_routes)}")
    for route in pulse_routes:
        print(f"  {route}")
    
    # Check if Pulse router is included
    print(f"\nRouter count: {len(APP.routes)}")
    for i, route in enumerate(APP.routes):
        print(f"  {i}: {type(route).__name__} - {getattr(route, 'prefix', 'no prefix')}")

if __name__ == "__main__":
    test_routes()