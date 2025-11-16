#!/usr/bin/env python
"""
Quick test to verify the setup is working.
Run this from Scripts/ folder to test conversion.
"""
import sys
import os

# Go to parent directory
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("Current directory:", os.getcwd())
print("Input folder exists:", os.path.exists("Input"))
print("Output folder exists:", os.path.exists("Output"))

from converter import collect_images, create_video_per_image_with_motion

# Test 1: collect images
images = collect_images("Input")
print(f"\nFound {len(images)} images:")
for img in images[:3]:
    print(f"  - {os.path.basename(img)}")

# Test 2: convert one image with motion effects
print("\nConverting with motion effects (testing basic conversion)...")
try:
    def progress_callback(current, total):
        percent = int((current / total) * 100)
        print(f"  {percent}%", end="\r")
    
    videos, metadata = create_video_per_image_with_motion("Input", "Output", motion_types=["none"], video_duration=3.0, fps=10, quality="720p", progress_callback=progress_callback)
    print("\n✓ Conversion successful!")
    
    # Check output
    print(f"\nGenerated {len(videos)} video files:")
    for v in videos[:3]:
        print(f"  - {v['filename']} ({v['size_mb']} MB)")
except Exception as e:
    print(f"✗ Conversion failed: {e}")
    import traceback
    traceback.print_exc()
