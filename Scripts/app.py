from flask import Flask, render_template, request, jsonify
from converter import create_video_per_image_with_motion
import threading
import os
import time
import subprocess
import sys
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')

# Get the Scripts directory path
script_dir = os.path.dirname(os.path.abspath(__file__))

# Job tracking
JOBS = {}

# Available motion effects
MOTION_EFFECTS = {
    'subtle': 'Subtle (Gentle Zoom + Pan)',
    'ken-burns': 'Ken Burns (Classic Cinema Zoom)',
    '360-pan': '360° Panoramic Pan',
    'tilt-shift': 'Tilt-Shift (Selective Focus)',
    'zoom-in': 'Zoom In (Strong)',
    'zoom-out': 'Zoom Out',
    'dolly-zoom': 'Dolly Zoom (Perspective)',
    'wave': 'Wave Distortion',
    'radial-blur': 'Radial Blur (Zoom Blur)',
    'rotation': 'Rotation (360°)',
    'flip': 'Flip with Zoom',
    'none': 'No Motion (Static)'
}

# Quality presets
QUALITY_OPTIONS = {
    '4K': '3840x2160',
    '1080p': '1920x1080',
    '720p': '1280x720',
    '480p': '854x480',
    '360p': '640x360'
}

def batch_worker(job_id, input_dir, motion_types, quality, fps, duration):
    """Background worker for batch conversion."""
    try:
        # Resolve input directory path
        if not os.path.isabs(input_dir):
            input_path = os.path.join(script_dir, input_dir)
        else:
            input_path = input_dir
        
        output_path = os.path.join(script_dir, 'Output')
        
        # Update job status
        JOBS[job_id]['status'] = 'running'
        
        def progress_callback(current, total):
            """Update job progress."""
            JOBS[job_id]['progress'] = int((current / total) * 100)
        
        # Create videos
        videos, metadata = create_video_per_image_with_motion(
            input_path,
            output_path,
            motion_types=motion_types,
            video_duration=float(duration),
            fps=int(fps),
            quality=quality,
            progress_callback=progress_callback
        )
        
        JOBS[job_id]['status'] = 'done'
        JOBS[job_id]['progress'] = 100
        JOBS[job_id]['output'] = videos
        JOBS[job_id]['metadata'] = metadata
        JOBS[job_id]['message'] = f"Successfully created {len(videos)} videos in {metadata['total_processing_time']}s"
    
    except Exception as e:
        JOBS[job_id]['status'] = 'error'
        JOBS[job_id]['message'] = str(e)

@app.route('/')
def index():
    """Serve the main UI."""
    return render_template('index.html')

@app.route('/api/effects')
def get_effects():
    """Get available motion effects."""
    return jsonify(MOTION_EFFECTS)

@app.route('/api/qualities')
def get_qualities():
    """Get available quality options."""
    return jsonify(QUALITY_OPTIONS)

@app.route('/batch-start', methods=['POST'])
def batch_start():
    """Start a batch conversion job."""
    data = request.get_json()
    input_dir = data.get('input_dir', 'Input')
    motion_types = data.get('motion_types', ['subtle'])
    quality = data.get('quality', '1080p')
    fps = data.get('fps', 10)
    duration = data.get('duration', 5)
    
    # Debug logging
    print(f"DEBUG: Received motion_types: {motion_types}, type: {type(motion_types)}")
    print(f"DEBUG: Received data: input_dir={input_dir}, quality={quality}, fps={fps}, duration={duration}")
    
    # Ensure motion_types is a list
    if isinstance(motion_types, str):
        motion_types = [motion_types]
    
    print(f"DEBUG: Final motion_types after conversion: {motion_types}")
    
    # Create job ID
    job_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    
    # Initialize job
    JOBS[job_id] = {
        'status': 'queued',
        'progress': 0,
        'output': [],
        'message': 'Job queued',
        'motion_types': motion_types,
        'quality': quality,
        'fps': fps,
        'duration': duration,
        'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Start background worker
    worker = threading.Thread(
        target=batch_worker,
        args=(job_id, input_dir, motion_types, quality, fps, duration),
        daemon=True
    )
    worker.start()
    
    return jsonify({'job_id': job_id})

@app.route('/status/<job_id>')
def status(job_id):
    """Get job status."""
    if job_id not in JOBS:
        return jsonify({'error': 'Job not found'}), 404
    
    job = JOBS[job_id]
    response = {
        'status': job['status'],
        'progress': job['progress'],
        'message': job['message'],
        'motion_types': job.get('motion_types', []),
        'quality': job.get('quality', 'unknown'),
        'fps': job.get('fps', 10),
        'duration': job.get('duration', 5),
        'output_count': len(job['output']),
        'start_time': job.get('start_time', '')
    }
    
    if job['status'] == 'done' and 'metadata' in job:
        response['metadata'] = job['metadata']
        if job['output']:
            response['videos'] = job['output']
    
    return jsonify(response)

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})


@app.route('/install-deps', methods=['POST'])
def install_deps():
    """Install Python dependencies from the root requirements.txt non-interactively.
    This endpoint is intended for local use only and will run pip install on the host.
    """
    requirements_path = os.path.join(script_dir, '..', 'requirements.txt')
    requirements_path = os.path.abspath(requirements_path)
    try:
        # Using sys.executable to ensure same Python is used
        proc = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', requirements_path],
                              capture_output=True, text=True, check=False)
        return jsonify({
            'returncode': proc.returncode,
            'stdout': proc.stdout,
            'stderr': proc.stderr
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(os.path.join(script_dir, 'Output'), exist_ok=True)
    os.makedirs(os.path.join(script_dir, 'Input'), exist_ok=True)
    os.makedirs(os.path.join(script_dir, 'static'), exist_ok=True)
    
    print(f"Starting Flask app from: {script_dir}")
    print(f"Input directory: {os.path.join(script_dir, 'Input')}")
    print(f"Output directory: {os.path.join(script_dir, 'Output')}")
    print(f"Available motion effects: {len(MOTION_EFFECTS)}")
    print(f"Available quality options: {len(QUALITY_OPTIONS)}")
    app.run(debug=False, port=5000, host='127.0.0.1')
