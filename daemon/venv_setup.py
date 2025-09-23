#!/usr/bin/env python3
"""
Virtual environment setup script for TexTeller LaTeX Predictor Daemon.
This script creates and configures a virtual environment for the daemon.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path


def create_venv():
    """Create a virtual environment for the daemon."""
    project_root = Path(__file__).parent.parent  # Go up one level from daemon/
    venv_path = project_root / "daemon_venv"
    
    print(f"Creating virtual environment at: {venv_path}")
    
    # Create virtual environment
    venv.create(venv_path, with_pip=True)
    
    # Get the correct pip path based on OS
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    print(f"Installing requirements in virtual environment...")
    
    # Install requirements
    requirements_path = Path(__file__).parent / "daemon_requirements.txt"
    try:
        subprocess.run([str(pip_path), "install", "-r", str(requirements_path)], check=True)
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False
    
    # Install the local texteller package in development mode
    print("Installing local texteller package...")
    try:
        subprocess.run([str(pip_path), "install", "-e", str(project_root)], check=True)
        print("✅ Local texteller package installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing local texteller package: {e}")
        return False
    
    print(f"✅ Virtual environment created successfully!")
    print(f"Python executable: {python_path}")
    print(f"Virtual environment path: {venv_path}")
    
    return True


def main():
    """Main function to set up the virtual environment."""
    print("TexTeller Daemon Virtual Environment Setup")
    print("=" * 50)
    
    if create_venv():
        print("\n🎉 Setup complete!")
        print("\nTo run the daemon with the virtual environment:")
        print("  python daemon/run_daemon.py")
        print("\nOr manually activate the environment:")
        if sys.platform == "win32":
            print("  daemon_venv\\Scripts\\activate")
        else:
            print("  source daemon_venv/bin/activate")
    else:
        print("\n❌ Setup failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
