#!/usr/bin/env python3
"""
Cleanup script for TexTeller LaTeX Predictor Daemon.
This script removes the virtual environment and cleans up temporary files.
"""

import os
import sys
import shutil
from pathlib import Path


def cleanup_venv():
    """Remove the virtual environment."""
    project_root = Path(__file__).parent.parent  # Go up one level from daemon/
    venv_path = project_root / "daemon_venv"
    
    if venv_path.exists():
        print(f"Removing virtual environment: {venv_path}")
        shutil.rmtree(venv_path)
        print("✅ Virtual environment removed")
    else:
        print("ℹ️  No virtual environment found")


def cleanup_temp_files():
    """Remove temporary files."""
    latex_file = Path("/tmp/latexPredict.png")
    
    if latex_file.exists():
        print(f"Removing temporary file: {latex_file}")
        latex_file.unlink()
        print("✅ Temporary file removed")
    else:
        print("ℹ️  No temporary files found")


def main():
    """Main cleanup function."""
    print("TexTeller Daemon Cleanup")
    print("=" * 30)
    print("⚠️  WARNING: This will PERMANENTLY DELETE the virtual environment!")
    print("   You will need to run 'python daemon/venv_setup.py' again to recreate it.")
    print()
    
    response = input("Are you sure you want to continue? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Cleanup cancelled.")
        return 0
    
    try:
        cleanup_venv()
        cleanup_temp_files()
        print("\n🎉 Cleanup complete!")
        print("All daemon files and virtual environment have been removed.")
        print("To recreate the environment, run: python daemon/venv_setup.py")
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
