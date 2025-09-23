#!/usr/bin/env python3
"""
Test script for the TexTeller LaTeX Predictor Daemon.
This script creates a test image and saves it to the monitored location.
"""

import os
import sys
import time
from pathlib import Path
import numpy as np
import cv2

def create_test_image():
    """Create a simple test image with mathematical content."""
    # Create a white background
    img = np.ones((200, 400, 3), dtype=np.uint8) * 255
    
    # Add some text to simulate a mathematical equation
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, 'E = mc^2', (50, 100), font, 1, (0, 0, 0), 2)
    cv2.putText(img, 'x^2 + y^2 = r^2', (50, 150), font, 0.7, (0, 0, 0), 2)
    
    return img

def main():
    """Test the daemon by creating a test image."""
    print("TexTeller Daemon Test Script")
    print("=" * 40)
    
    # Use /tmp directory
    test_image_path = Path("/tmp/latexPredict.png")
    
    print(f"Creating test image at: {test_image_path}")
    
    # Create and save test image
    test_img = create_test_image()
    cv2.imwrite(str(test_image_path), test_img)
    
    print("Test image created successfully!")
    print("If the daemon is running, it should detect this change and process the image.")
    print("Check the daemon output for the prediction result.")
    
    # Wait a moment for the daemon to process
    print("\nWaiting 5 seconds for daemon to process...")
    time.sleep(5)
    
    print("Test completed!")
    print("You can also manually replace the image file to test again.")

if __name__ == "__main__":
    main()
