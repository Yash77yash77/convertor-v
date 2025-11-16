import cv2
import os

# Check if we can read one of the created videos
import os as __os
__script_dir = __os.path.dirname(__os.path.abspath(__file__))
video_path = __os.path.join(__script_dir, "Output", "IMG_4707_motion_zoom-in_480p.avi")

if os.path.exists(video_path):
    cap = cv2.VideoCapture(video_path)
    
    if cap.isOpened():
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        print(f"Video Properties:")
        print(f"  Frames: {frame_count}")
        print(f"  FPS: {fps}")
        print(f"  Resolution: {width}x{height}")
        print(f"  Duration: {frame_count/fps:.2f}s")
        
        # Check first, middle, and last frames to see if they differ (indicating motion)
        frames_to_check = [0, frame_count//2, frame_count-1]
        frame_data = []
        
        for idx in frames_to_check:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                # Calculate frame hash to compare
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                hash_val = hash(gray.tobytes())
                frame_data.append((idx, hash_val))
        
        cap.release()
        
        print(f"\nFrame Data (for motion detection):")
        for frame_idx, frame_hash in frame_data:
            print(f"  Frame {frame_idx}: hash={frame_hash}")
        
        # If hashes differ, motion is present
        if len(frame_data) > 1:
            hashes_differ = len(set(h for _, h in frame_data)) > 1
            print(f"\nFrames differ (motion detected): {hashes_differ}")
    else:
        print("Failed to open video")
else:
    print("Video file not found")
