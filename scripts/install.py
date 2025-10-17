#!/usr/bin/env python3
"""
Installation script for Apex Orchestrator
"""

import subprocess
import sys
import pathlib

def install_requirements():
    """Install required packages"""
    requirements_file = pathlib.Path(__file__).parent.parent / "requirements.txt"
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])

def setup_directories():
    """Create necessary directories"""
    project_root = pathlib.Path(__file__).parent.parent
    directories = ["logs", "C:\\ApexWork"]
    
    for directory in directories:
        dir_path = pathlib.Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")

if __name__ == "__main__":
    print("Installing Apex Orchestrator...")
    install_requirements()
    setup_directories()
    print("Installation complete!")

