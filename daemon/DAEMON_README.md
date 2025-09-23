# TexTeller LaTeX Predictor Daemon

This is a high-level script that solves the model loading performance issue by loading the TexTeller model once at startup and then monitoring a file for changes to make predictions.

## Features

- **One-time model loading**: The model is loaded once when the daemon starts, eliminating the loading time for each prediction
- **File monitoring**: Automatically detects changes to `/tmp/latexPredict.png`
- **Automatic prediction**: When the file changes, it immediately makes a LaTeX prediction
- **Clipboard integration**: Automatically copies the prediction result to your clipboard
- **Desktop notifications**: Uses `notify-send` to inform you when processing starts and completes
- **Cross-platform**: Works on Linux, macOS, and Windows

## Setup

The daemon uses a virtual environment to avoid conflicts with your system Python installation.

### Quick Setup

**Linux/macOS:**
```bash
bash safe_setup_daemon.sh
```

**Windows:**
```cmd
setup_daemon.bat
```

### Manual Setup

1. Create virtual environment and install dependencies:
   ```bash
   python venv_setup.py
   ```

2. For Linux users, install required utilities:
   ```bash
   sudo apt install xclip libnotify-bin  # or xsel instead of xclip
   ```

3. Make scripts executable (Linux/macOS):
   ```bash
   chmod +x run_daemon.py run_test.py venv_setup.py
   ```

## Usage

1. Start the daemon:
   ```bash
   python run_daemon.py
   # or legacy wrapper
   python run_optimized_daemon.py
   ```

2. The daemon will start and display:
   ```
   Loading TexTeller model...
   Model loaded successfully on device: cuda:0
   Monitoring directory: /home/username/.temp
   Waiting for changes to latexPredict.png...
   Press Ctrl+C to stop.
   ```
   
   You'll also receive a desktop notification confirming the daemon is ready.

3. To make a prediction:
   - Save an image as `/tmp/latexPredict.png`
   - You'll receive a notification that processing has started
   - The daemon will automatically detect the change and process the image
   - When complete, you'll receive a success notification and the LaTeX prediction will be copied to your clipboard

4. Stop the daemon:
   - Press `Ctrl+C`

5. Run tests:
   ```bash
   python run_test.py
   ```

6. Benchmark performance:
   ```bash
   python benchmark_daemon.py
   ```

## Virtual Environment Lifecycle

The virtual environment is designed to persist and be reused:

- **Creation**: `python venv_setup.py` creates the environment once
- **Activation**: `python run_daemon.py` automatically activates it
- **Deactivation**: When daemon stops, environment is deactivated but remains available
- **Reuse**: Next time you run the daemon, it uses the same environment
- **Cleanup**: `python cleanup_daemon.py` permanently removes the environment (with confirmation)

## How it Works

1. **Model Loading**: The daemon loads the TexTeller model and tokenizer once at startup using the standard PyTorch backend (we can revisit ONNX later)
2. **File Monitoring**: Uses the `watchdog` library to monitor the `/tmp` directory for file changes
3. **Notification**: Sends a desktop notification when processing starts
4. **Prediction**: When `latexPredict.png` is modified, it runs the prediction using the pre-loaded model
5. **Clipboard**: Copies the result to the system clipboard using platform-specific utilities
6. **Completion Notification**: Sends a success notification when processing is complete

## Virtual Environment Benefits

- **Isolated dependencies**: No conflicts with your system Python packages
- **Clean installation**: All dependencies are contained within the project
- **Persistent environment**: Virtual environment remains available after daemon stops
- **No terminal pollution**: Running the daemon doesn't affect your terminal's Python environment
- **Reproducible setup**: Same environment every time, regardless of your system configuration
- **Easy management**: Virtual environment is automatically activated/deactivated as needed

## Performance Optimizations

The optimized daemon includes several performance improvements:

### **Model Compilation**
- **PyTorch 2.0+ Compilation**: Uses `torch.compile()` for faster inference
- **ONNX Runtime**: Optimized execution providers for CPU/GPU
- **Memory Optimization**: Efficient attention mechanisms and memory usage

### **Runtime Optimizations**
- **Model Warmup**: Pre-runs inference to optimize first prediction
- **CUDA Optimizations**: Enables cuDNN benchmark mode for consistent input sizes
- **Thread Optimization**: Optimal CPU thread count for inference
- **Memory Management**: Uses `torch.no_grad()` to reduce memory usage

### **System Optimizations**
- **Persistent Environment**: Virtual environment stays loaded between runs
- **File Monitoring**: Efficient file change detection with debouncing
- **Batch Processing**: Optimized for single-image processing

## Performance Benefits

- **Eliminates model loading time**: The model is loaded only once at startup
- **Fast inference**: Uses ONNX runtime with compilation optimizations
- **Immediate response**: File monitoring provides instant detection of changes
- **No repeated initialization**: All components are initialized once and reused
- **Compiled execution**: Model compilation can provide 1.5-3x speedup

## Troubleshooting

- **Clipboard not working**: Make sure you have `xclip` or `xsel` installed on Linux
- **Notifications not working**: Make sure you have `libnotify-bin` installed on Linux
- **Permission errors**: Ensure the script is executable (`chmod +x run_daemon.py`)
- **Model loading errors**: Make sure the virtual environment is set up (`python venv_setup.py`)
- **File not detected**: Check that the file is saved as `latexPredict.png` in `/tmp/`
- **Virtual environment issues**: If the environment is corrupted, run `python cleanup_daemon.py` then `python venv_setup.py`

## Dependencies

All dependencies are included in `daemon_requirements.txt`:

**Core Dependencies:**
- `click>=8.1.8` - CLI framework
- `colorama>=0.4.6` - Cross-platform colored terminal text
- `opencv-python-headless>=4.11.0.86` - Computer vision library
- `pyclipper>=1.3.0.post6` - Polygon clipping library
- `shapely>=2.1.0` - Geometric objects library
- `torch>=2.6.0` - PyTorch deep learning framework
- `torchvision>=0.21.0` - PyTorch vision utilities
- `transformers==4.47` - Hugging Face transformers
- `wget>=3.2` - File downloading utility
- `optimum[onnxruntime]>=1.24.0` - ONNX optimization

**Daemon-Specific Dependencies:**
- `watchdog>=3.0.0` - File system monitoring

**System Dependencies (Linux):**
- `xclip` or `xsel` - Clipboard utilities
- `libnotify-bin` - Desktop notifications

**Optional:**
- `onnxruntime-gpu>=1.21.0` - GPU acceleration (uncomment in requirements if you have CUDA)
