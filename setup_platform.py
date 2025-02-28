#!/usr/bin/env python3
"""
Platform-specific setup script for TexTeller.
This script detects the platform and installs the appropriate version of onnxruntime.
"""

import platform
import subprocess
import sys


def install_platform_specific_dependencies():
    """Install the appropriate version of onnxruntime based on the platform."""
    system = platform.system().lower()

    if system == "linux":
        print("Linux detected. Installing onnxruntime-gpu...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "onnxruntime-gpu>=1.20.0"])
    else:
        print(f"{system.capitalize()} detected. Installing onnxruntime...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "onnxruntime>=1.20.0"])

    print("Platform-specific dependencies installed successfully.")


if __name__ == "__main__":
    install_platform_specific_dependencies()
