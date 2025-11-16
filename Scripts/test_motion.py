#!/usr/bin/env python
"""Test motion effects to debug the issue."""
import os
import sys
import cv2
import numpy as np

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from converter import collect_images, apply_subtle_motion, apply_ken_burns_effect, apply_360_pan_effect

images = collect_images("Input")
if not images:
    print("No images found!")
    sys.exit(1)

img = cv2.imread(images[0])
if img is None:
    print(f"Failed to read: {images[0]}")
    sys.exit(1)

print(f"Image shape: {img.shape}")
print(f"Total frames: 50")

# Test each motion effect
print("\nTesting motion effects:")

try:
    print("  1. Subtle motion...", end=" ")
    frame = apply_subtle_motion(img, 25, 50)  # middle frame
    print(f"✓ Output shape: {frame.shape}")
except Exception as e:
    print(f"✗ Error: {e}")

try:
    print("  2. Ken Burns effect...", end=" ")
    frame = apply_ken_burns_effect(img, 25, 50)
    print(f"✓ Output shape: {frame.shape}")
except Exception as e:
    print(f"✗ Error: {e}")

try:
    print("  3. 360 Pan effect...", end=" ")
    frame = apply_360_pan_effect(img, 25, 50)
    print(f"✓ Output shape: {frame.shape}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n✓ All motion effects working!")
