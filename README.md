# Image → Video converter (local)

This small app reads images from an input folder and composes a 5-second MP4 (50 frames). It provides a small web UI to start the conversion and monitor progress.

Requirements
- Python 3.8+
- Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

How to run (Windows)
1. Put your images into `Scripts\Input` (or any folder — you can type its path in the UI).
2. Start the app:

```powershell
	python app.py
```

3. Open http://127.0.0.1:5000 in your browser.
4. Enter the input folder path and click "Start Conversion".

- Notes
- The converter will pick images by filename sorting. If there are fewer than 50 images they will be repeated to reach 50 frames; if there are more, only the first 50 (after sorting) are used.
- Output is written to the `output/` directory.

Demo images
- If you don't have images, generate 50 demo frames with:

```powershell
python generate_demo_images.py
```

This will create 50 PNG frames in `./input` so you can test the converter end-to-end.

Windows single-click
---------------------
If you'd like a one-click launcher, run `start_server.bat` from the project root — it will create a small virtualenv, install dependencies from `requirements.txt`, and start the Flask server for you.

Supported formats and HEIC
-------------------------
OpenCV supports common formats like PNG and JPEG. If OpenCV fails to read a file (for example, HEIC), the converter will attempt to open it with Pillow. To add HEIC support install `pillow-heif`:

```powershell
venv\Scripts\Activate.ps1
pip install pillow-heif
```

Then re-run the server.

One-click start scripts (Windows)
---------------------------------
The repository provides `start.bat` (Command Prompt) and `start.ps1` (PowerShell) at the project root. These will:

- Create/activate a virtual environment in `.venv` (if missing)
- Install dependencies from `requirements.txt` automatically
- Start the Flask server at `http://127.0.0.1:5000`

Use PowerShell as follows to open the UI in your browser automatically:

```powershell
./start.ps1 -OpenBrowser
```

Or from a normal Command Prompt:

```cmd
start.bat
```
