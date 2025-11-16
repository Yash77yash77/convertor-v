import cv2
import numpy as np
import os
try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False
import glob
from datetime import datetime

# Quality presets: (width, height, bitrate_factor)
QUALITY_PRESETS = {
    '4K': (3840, 2160, 1.5),
    '1080p': (1920, 1080, 1.0),
    '720p': (1280, 720, 0.7),
    '480p': (854, 480, 0.5),
    '360p': (640, 360, 0.3),
}

def collect_images(input_dir):
    """Collect all image files from input directory in sorted order."""
    if not os.path.exists(input_dir):
        return []
    
    # Include HEIC in case user has Apple HEIC images. If not installed, files will be skipped.
    image_patterns = ['*.png', '*.jpg', '*.jpeg', '*.bmp', '*.tiff', '*.heic']
    images = []
    
    for pattern in image_patterns:
        images.extend(glob.glob(os.path.join(input_dir, pattern)))
    
    return sorted(images)

def apply_subtle_motion(img, frame_idx, total_frames):
    """Apply subtle zoom and circular pan motion."""
    height, width = img.shape[:2]
    progress = frame_idx / max(total_frames - 1, 1)
    
    # Subtle zoom (1.0 -> 1.15)
    zoom = 1.0 + 0.15 * progress
    
    # Circular pan
    pan_x = int(20 * np.sin(progress * np.pi * 2))
    pan_y = int(15 * np.cos(progress * np.pi * 2))
    
    # Create transformation matrix
    center = (width // 2, height // 2)
    M = cv2.getRotationMatrix2D(center, 0, zoom)
    M[0, 2] += pan_x
    M[1, 2] += pan_y
    
    # Apply transformation
    transformed = cv2.warpAffine(img, M, (width, height), borderMode=cv2.BORDER_REFLECT)
    return transformed

def apply_ken_burns_effect(img, frame_idx, total_frames):
    """Apply Ken Burns zoom and pan effect."""
    height, width = img.shape[:2]
    progress = frame_idx / max(total_frames - 1, 1)
    
    # Progressive zoom (1.0 -> 1.3)
    zoom = 1.0 + 0.3 * (progress ** 2)
    
    # Sinusoidal pan
    pan_x = int(30 * np.sin(progress * np.pi))
    pan_y = int(25 * (progress - 0.5))
    
    center = (width // 2, height // 2)
    M = cv2.getRotationMatrix2D(center, 0, zoom)
    M[0, 2] += pan_x
    M[1, 2] += pan_y
    
    transformed = cv2.warpAffine(img, M, (width, height), borderMode=cv2.BORDER_REFLECT)
    return transformed

def apply_360_pan_effect(img, frame_idx, total_frames):
    """Apply 360-degree panoramic pan effect by tiling and panning."""
    height, width = img.shape[:2]
    progress = frame_idx / max(total_frames - 1, 1)
    
    # Create a 3x wide tiled version for continuous panoramic pan
    tiled = np.hstack([img, img, img])
    tiled_width = tiled.shape[1]
    
    # Pan from left to right across tiled image
    start_x = int((tiled_width - width) * progress)
    
    # Extract window
    panned = tiled[:, start_x:start_x + width]
    
    return panned

def apply_tilt_shift_effect(img, frame_idx, total_frames):
    """Apply tilt-shift (selective focus) effect with zoom."""
    height, width = img.shape[:2]
    progress = frame_idx / max(total_frames - 1, 1)
    
    # Zoom effect
    zoom = 1.0 + 0.2 * progress
    center = (width // 2, height // 2)
    M = cv2.getRotationMatrix2D(center, 0, zoom)
    transformed = cv2.warpAffine(img, M, (width, height), borderMode=cv2.BORDER_REFLECT)
    
    # Tilt-shift blur (focus on horizontal band)
    blurred = cv2.GaussianBlur(transformed, (21, 21), 0)
    focus_band = int(height * 0.4)
    mask = np.zeros((height, 1), dtype=np.float32)
    mask[focus_band:focus_band + int(height * 0.2)] = 1.0
    
    # Smooth transition
    for i in range(focus_band):
        mask[i] = max(0, (i - (focus_band - int(height * 0.15))) / int(height * 0.15))
    for i in range(focus_band + int(height * 0.2), height):
        mask[i] = max(0, ((focus_band + int(height * 0.35) - i) / int(height * 0.15)))
    
    mask = np.tile(mask, (1, width))
    result = (transformed * mask + blurred * (1 - mask)).astype(np.uint8)
    return result


def read_image_with_fallback(path):
    """Attempt to read image using OpenCV first; if it fails and Pillow is available try that.

    Returns a BGR numpy array (as OpenCV uses BGR) or None on failure.
    """
    # Try OpenCV
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is not None:
        # Convert transparency to BGR if needed
        if img.ndim == 3 and img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    # If OpenCV failed and Pillow is available, try Pillow
    if PIL_AVAILABLE:
        try:
            # Try to register HEIF plugin if pillow_heif is available
            if path.lower().endswith('.heic'):
                try:
                    import pillow_heif
                    pillow_heif.register_heif_opener()
                except Exception:
                    # pillow-heif may not be available; pillow may still fail gracefully
                    pass

            from PIL import Image
            pil_img = Image.open(path).convert('RGB')
            arr = np.array(pil_img)
            # PIL gives RGB, convert to BGR for OpenCV
            img = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            return img
        except Exception:
            return None

    return None

def apply_zoom_in_effect(img, frame_idx, total_frames):
    """Apply continuous zoom-in effect."""
    height, width = img.shape[:2]
    progress = frame_idx / max(total_frames - 1, 1)
    
    # Strong zoom (1.0 -> 2.0)
    zoom = 1.0 + 1.0 * progress
    
    center = (width // 2, height // 2)
    M = cv2.getRotationMatrix2D(center, 0, zoom)
    transformed = cv2.warpAffine(img, M, (width, height), borderMode=cv2.BORDER_REFLECT)
    return transformed

def apply_zoom_out_effect(img, frame_idx, total_frames):
    """Apply continuous zoom-out effect."""
    height, width = img.shape[:2]
    progress = frame_idx / max(total_frames - 1, 1)
    
    # Zoom out (1.2 -> 1.0)
    zoom = 1.2 - 0.2 * progress
    
    center = (width // 2, height // 2)
    M = cv2.getRotationMatrix2D(center, 0, zoom)
    transformed = cv2.warpAffine(img, M, (width, height), borderMode=cv2.BORDER_REFLECT)
    return transformed

def apply_dolly_zoom_effect(img, frame_idx, total_frames):
    """Apply Dolly Zoom (perspective distortion) effect."""
    height, width = img.shape[:2]
    progress = frame_idx / max(total_frames - 1, 1)
    
    # Dynamic zoom and distortion
    zoom = 1.0 + 0.5 * np.sin(progress * np.pi)
    
    center = (width // 2, height // 2)
    M = cv2.getRotationMatrix2D(center, 0, zoom)
    
    # Add slight rotation
    angle = 5 * np.sin(progress * np.pi * 2)
    rotation_M = cv2.getRotationMatrix2D(center, angle, 1.0)
    transformed = cv2.warpAffine(img, rotation_M, (width, height), borderMode=cv2.BORDER_REFLECT)
    transformed = cv2.warpAffine(transformed, M, (width, height), borderMode=cv2.BORDER_REFLECT)
    
    return transformed

def apply_wave_effect(img, frame_idx, total_frames):
    """Apply wave distortion effect."""
    height, width = img.shape[:2]
    progress = frame_idx / max(total_frames - 1, 1)
    
    # Create wave distortion
    x, y = np.meshgrid(np.arange(width), np.arange(height))
    
    # Wave parameters
    wave_freq = 0.01
    wave_amp = 20 * progress
    
    x_wave = x + wave_amp * np.sin(y * wave_freq + progress * np.pi * 2)
    y_wave = y + wave_amp * np.cos(x * wave_freq + progress * np.pi * 2)
    
    # Clip to valid range
    x_wave = np.clip(x_wave, 0, width - 1).astype(np.float32)
    y_wave = np.clip(y_wave, 0, height - 1).astype(np.float32)
    
    # Remap
    result = cv2.remap(img, x_wave, y_wave, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return result

def apply_radial_blur_effect(img, frame_idx, total_frames):
    """Apply radial blur (zoom blur) effect."""
    height, width = img.shape[:2]
    progress = frame_idx / max(total_frames - 1, 1)
    
    center = (width // 2, height // 2)
    
    # Create motion blur effect radiating from center
    result = img.astype(np.float32)
    blur_strength = int(1 + 4 * progress)
    
    for i in range(blur_strength):
        scale = 1.0 + 0.05 * i
        M = cv2.getRotationMatrix2D(center, 0, scale)
        zoomed = cv2.warpAffine(img.astype(np.float32), M, (width, height), 
                               borderMode=cv2.BORDER_REFLECT)
        result += zoomed
    
    result = (result / (blur_strength + 1)).astype(np.uint8)
    return result

def apply_rotation_effect(img, frame_idx, total_frames):
    """Apply smooth rotation effect."""
    height, width = img.shape[:2]
    progress = frame_idx / max(total_frames - 1, 1)
    
    # Full rotation (360 degrees)
    angle = 360 * progress
    
    center = (width // 2, height // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    transformed = cv2.warpAffine(img, M, (width, height), borderMode=cv2.BORDER_REFLECT)
    
    return transformed

def apply_flip_effect(img, frame_idx, total_frames):
    """Apply flip effect with zoom."""
    height, width = img.shape[:2]
    progress = frame_idx / max(total_frames - 1, 1)
    
    # Alternate flips with zoom
    flips = int(progress * 3)
    result = img.copy()
    
    if flips % 2 == 1:
        result = cv2.flip(result, 1)  # Horizontal flip
    
    zoom = 1.0 + 0.2 * np.sin(progress * np.pi * 2)
    center = (width // 2, height // 2)
    M = cv2.getRotationMatrix2D(center, 0, zoom)
    result = cv2.warpAffine(result, M, (width, height), borderMode=cv2.BORDER_REFLECT)
    
    return result

def create_video_per_image_with_motion(input_dir, output_dir, motion_types=['subtle'], 
                                       video_duration=5.0, fps=10, quality='1080p',
                                       progress_callback=None):
    """
    Convert each input image into a separate video with motion effects.
    
    Args:
        input_dir: Directory containing input images
        output_dir: Directory for output videos
        motion_types: List of motion types to apply in sequence (can be 1-3)
                     Options: 'subtle', 'ken-burns', '360-pan', 'tilt-shift', 
                             'zoom-in', 'zoom-out', 'dolly-zoom', 'wave', 
                             'radial-blur', 'rotation', 'flip', 'none'
        video_duration: Duration of each video in seconds
        fps: Frames per second
        quality: Quality preset ('4K', '1080p', '720p', '480p', '360p')
        progress_callback: Function to call with (current, total) for progress tracking
    
    Returns:
        List of created video file paths with metadata
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Get target resolution from quality preset
    if quality not in QUALITY_PRESETS:
        quality = '1080p'
    width, height, _ = QUALITY_PRESETS[quality]
    target_size = (width, height)
    
    images = collect_images(input_dir)
    if not images:
        return []
    
    total_images = len(images)
    total_frames = int(video_duration * fps)
    created_videos = []
    
    # Normalize motion_types to list
    if isinstance(motion_types, str):
        motion_types = [motion_types]
    else:
        motion_types = list(motion_types)[:3]  # Max 3 effects
    
    # Motion function mapping
    motion_functions = {
        'subtle': apply_subtle_motion,
        'ken-burns': apply_ken_burns_effect,
        '360-pan': apply_360_pan_effect,
        'tilt-shift': apply_tilt_shift_effect,
        'zoom-in': apply_zoom_in_effect,
        'zoom-out': apply_zoom_out_effect,
        'dolly-zoom': apply_dolly_zoom_effect,
        'wave': apply_wave_effect,
        'radial-blur': apply_radial_blur_effect,
        'rotation': apply_rotation_effect,
        'flip': apply_flip_effect,
        'none': None
    }
    
    # Validate motion types
    motion_types = [mt for mt in motion_types if mt in motion_functions]
    if not motion_types:
        motion_types = ['none']
    
    start_time = datetime.now()
    
    for img_idx, img_path in enumerate(images):
        # Read and prepare image
        # Use fallback image loader which tries cv2 then Pillow
        img = read_image_with_fallback(img_path)
        if img is None and PIL_AVAILABLE:
            try:
                pil_img = Image.open(img_path).convert('RGB')
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            except Exception as e:
                print(f"Skipping '{img_path}': {e}")
                continue
        elif img is None:
            print(f"Skipping '{img_path}' - OpenCV couldn't read it (Pillow not available for fallback)")
            continue
        
        # Resize to target
        img = cv2.resize(img, target_size, interpolation=cv2.INTER_LANCZOS4)
        
        # Create video writer (using XVID codec for Windows compatibility)
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        motion_suffix = '_'.join(motion_types[:3])
        output_path = os.path.join(output_dir, f"{base_name}_motion_{motion_suffix}_{quality}.avi")
        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        writer = cv2.VideoWriter(output_path, fourcc, fps, target_size)
        
        # Generate frames with motion effects divided equally by time
        for frame_idx in range(total_frames):
            frame = img.copy()
            
            # Determine which effect segment this frame belongs to
            segment_duration = total_frames / len(motion_types)
            current_segment = int(frame_idx / segment_duration)
            current_segment = min(current_segment, len(motion_types) - 1)  # Clamp to last segment
            
            # Get the motion type for this segment
            motion_type = motion_types[current_segment]
            
            # Apply the effect for this segment
            if motion_type in motion_functions and motion_functions[motion_type] is not None:
                motion_func = motion_functions[motion_type]
                # Frame progress within this effect's segment (0.0 to 1.0)
                segment_start = int(current_segment * segment_duration)
                segment_end = int((current_segment + 1) * segment_duration)
                frame_in_segment = frame_idx - segment_start
                frames_in_segment = segment_end - segment_start
                
                # Apply effect with progress relative to segment
                frame = motion_func(frame, frame_in_segment, frames_in_segment)
            
            # Ensure frame is 3-channel BGR
            if len(frame.shape) == 2:
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            elif frame.shape[2] == 4:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            writer.write(frame.astype(np.uint8))
        
        writer.release()
        
        # Calculate file size and time generated
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        time_generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        video_info = {
            'path': output_path,
            'filename': os.path.basename(output_path),
            'size_mb': round(file_size, 2),
            'duration_seconds': video_duration,
            'fps': fps,
            'quality': quality,
            'resolution': f"{target_size[0]}x{target_size[1]}",
            'motion_effects': motion_types,
            'time_generated': time_generated,
            'speed': f"{fps}fps"
        }
        
        created_videos.append(video_info)
        
        # Call progress callback
        if progress_callback:
            progress_callback(img_idx + 1, total_images)
    
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()
    
    return created_videos, {
        'start_time': start_time.strftime("%Y-%m-%d %H:%M:%S"),
        'end_time': end_time.strftime("%Y-%m-%d %H:%M:%S"),
        'total_processing_time': round(processing_time, 2),
        'videos_created': len(created_videos),
        'quality': quality,
        'motion_effects': motion_types
    }

if __name__ == '__main__':
    # Test the converter
    input_dir = 'Input'
    output_dir = 'Output'
    
    print(f"Converting images from {input_dir} to {output_dir}...")
    videos, metadata = create_video_per_image_with_motion(
        input_dir, output_dir, 
        motion_types=['subtle', 'zoom-in'],
        quality='1080p'
    )
    print(f"\nMetadata:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    print(f"\nCreated {len(videos)} videos:")
    for v in videos[:3]:
        print(f"  - {v['filename']} ({v['size_mb']} MB) - {v['time_generated']}")
