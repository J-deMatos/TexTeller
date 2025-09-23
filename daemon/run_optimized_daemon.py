#!/usr/bin/env python3
"""
Launcher script for Optimized TexTeller LaTeX Predictor Daemon with virtual environment.
This script automatically activates the virtual environment, runs the optimized daemon,
and deactivates it without affecting the user's terminal environment.
"""

import os
import sys
import subprocess
from pathlib import Path


def get_venv_paths():
    """Get the virtual environment paths based on the operating system."""
    project_root = Path(__file__).parent.parent  # Go up one level from daemon/
    venv_path = project_root / "daemon_venv"
    
    if sys.platform == "win32":
        python_path = venv_path / "Scripts" / "python.exe"
        activate_script = venv_path / "Scripts" / "activate.bat"
    else:
        python_path = venv_path / "bin" / "python"
        activate_script = venv_path / "bin" / "activate"
    
    return venv_path, python_path, activate_script


def check_venv_exists():
    """Check if the virtual environment exists."""
    venv_path, python_path, _ = get_venv_paths()
    
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


def run_optimized_daemon():
    """Legacy wrapper: delegate to unified daemon using the virtual environment."""
    if not check_venv_exists():
        return 1
    
    venv_path, python_path, _ = get_venv_paths()
    # Delegate to unified daemon
    daemon_script = Path(__file__).parent / "latex_predictor_daemon.py"
    
    print("⚡ Starting TexTeller LaTeX Predictor Daemon (unified)...")
    print(f"Using virtual environment: {venv_path}")
    print("=" * 60)
    
    try:
        # Run the unified daemon using the virtual environment's Python
        # The virtual environment is automatically activated for this process
        subprocess.run([str(python_path), str(daemon_script)], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Daemon stopped by user")
        print("Virtual environment remains available for future use")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running daemon: {e}")
        print("Virtual environment remains available for future use")
        return 1
    except FileNotFoundError:
        print(f"❌ Daemon script not found: {daemon_script}")
        return 1
    
    print("✅ Daemon stopped")
    print("Virtual environment remains available for future use")
    return 0


def main():
    """Main function to run the optimized daemon."""
    return run_optimized_daemon()


if __name__ == "__main__":
    sys.exit(main())
