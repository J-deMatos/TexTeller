#!/usr/bin/env python3
"""
Test script launcher for TexTeller LaTeX Predictor Daemon with virtual environment.
This script automatically activates the virtual environment, runs the test,
and deactivates it without affecting the user's terminal environment.
"""

import os
import sys
import subprocess
from pathlib import Path


def get_venv_paths():
    """Get the virtual environment paths based on the operating system."""
    project_root = Path(__file__).parent.parent  # Go up one level from tests/
    venv_path = project_root / "daemon_venv"
    
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        python_path = venv_path / "bin" / "python"
    
    return venv_path, python_path


def check_venv_exists():
    """Check if the virtual environment exists."""
    venv_path, python_path = get_venv_paths()
    
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("Please run the setup script first:")
        print("  python daemon/venv_setup.py")
        return False
    
    if not python_path.exists():
        print("❌ Python executable not found in virtual environment!")
        print("Please recreate the virtual environment:")
        print("  python daemon/venv_setup.py")
        return False
    
    return True


def run_test():
    """Run the test using the virtual environment."""
    if not check_venv_exists():
        return 1
    
    venv_path, python_path = get_venv_paths()
    test_script = Path(__file__).parent / "test_daemon.py"
    
    print("🧪 Running TexTeller Daemon Test...")
    print(f"Using virtual environment: {venv_path}")
    print("=" * 50)
    
    try:
        # Run the test using the virtual environment's Python
        # The virtual environment is automatically activated for this process
        subprocess.run([str(python_path), str(test_script)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running test: {e}")
        print("Virtual environment remains available for future use")
        return 1
    except FileNotFoundError:
        print(f"❌ Test script not found: {test_script}")
        return 1
    
    print("✅ Test completed")
    print("Virtual environment remains available for future use")
    return 0


def main():
    """Main function to run the test."""
    return run_test()


if __name__ == "__main__":
    sys.exit(main())
