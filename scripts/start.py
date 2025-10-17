#!/usr/bin/env python3
"""
Startup script for Apex Orchestrator with graceful shutdown handling
"""

import sys
import pathlib
import signal
import logging
import uvicorn
import os

# Add src directory to path
src_dir = pathlib.Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

logger = logging.getLogger("apex_orchestrator")

def handle_shutdown(signum, frame):
    """Handle graceful shutdown on SIGTERM/SIGINT"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)
    
    # Get environment
    environment = os.getenv("ENVIRONMENT", "development")
    
    # Configuration based on environment
    config = {
        "app": "main:APP",
        "host": "0.0.0.0",
        "port": int(os.getenv("PORT", "8000")),
        "log_level": "info",
        "access_log": True,
    }
    
    if environment == "development":
        # Development mode: enable auto-reload
        config.update({
            "reload": True,
            "reload_dirs": [str(src_dir)],
        })
        logger.info("Starting in DEVELOPMENT mode with auto-reload")
    else:
        # Production mode: multiple workers, no reload
        config.update({
            "workers": int(os.getenv("WORKERS", "2")),
            "reload": False,
        })
        logger.info(f"Starting in PRODUCTION mode with {config['workers']} workers")
    
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        logger.info("Shutdown initiated by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
