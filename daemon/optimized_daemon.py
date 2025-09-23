#!/usr/bin/env python3
"""
Optimized TexTeller LaTeX Predictor Daemon with performance improvements.
This version includes compilation optimizations, caching, and other speedups.
Monitors /tmp/latexPredict.png for changes.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from texteller.api import load_model, load_tokenizer, img2latex
from texteller.utils import get_device
from texteller.models import TexTeller
from texteller.globals import Globals
import torch
import numpy as np

# Import ONNX model type for type checking
try:
    from optimum.onnxruntime import ORTModelForVision2Seq
except ImportError:
    ORTModelForVision2Seq = None


class OptimizedLatexPredictorHandler(FileSystemEventHandler):
    """Optimized file system event handler with performance improvements."""
    
    def __init__(self, model, tokenizer, device, target_file_path):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.target_file_path = str(target_file_path)
        self.last_modified = 0
        
        # Performance optimizations
        self._setup_optimizations()
        
    def _setup_optimizations(self):
        """Set up various performance optimizations."""
        # Enable optimizations for PyTorch
        if hasattr(torch, 'backends'):
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False
        
        # Set optimal thread count for CPU inference
        if self.device.type == 'cpu':
            torch.set_num_threads(min(4, os.cpu_count() or 1))
        
        # Enable memory efficient attention if available
        if hasattr(torch.nn.functional, 'scaled_dot_product_attention'):
            torch.backends.cuda.enable_flash_sdp(True)
        
        # Compile model for faster inference (PyTorch 2.0+)
        if hasattr(torch, 'compile') and (ORTModelForVision2Seq is None or not isinstance(self.model, ORTModelForVision2Seq)):
            try:
                print("🔥 Compiling model with torch.compile for faster inference...")
                self.model = torch.compile(self.model, mode="reduce-overhead")
                print("✅ Model compilation completed!")
            except Exception as e:
                print(f"⚠️  Model compilation failed: {e}")
                print("Continuing with uncompiled model...")
        
        # Warm up the model with a dummy inference (skip for ONNX models)
        if not isinstance(self.model, ORTModelForVision2Seq):
            self._warmup_model()
        else:
            print("🔥 Skipping warmup for ONNX model (not needed)")
        
    def _warmup_model(self):
        """Warm up the model with a dummy inference to optimize first run."""
        try:
            print("🔥 Warming up model...")
            dummy_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            
            # Run a dummy inference to warm up the model
            with torch.no_grad():
                _ = img2latex(
                    model=self.model,
                    tokenizer=self.tokenizer,
                    images=[dummy_image],
                    device=self.device,
                    out_format="katex",
                    keep_style=False,
                    num_beams=1
                )
            print("✅ Model warmup completed!")
        except Exception as e:
            print(f"⚠️  Model warmup failed: {e}")
        
    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return
            
        file_path = event.src_path
        # Only process if it's exactly our target file
        if file_path == self.target_file_path:
            # Check if file was actually modified (not just accessed)
            current_time = os.path.getmtime(file_path)
            if current_time > self.last_modified + 1:  # 1 second debounce
                self.last_modified = current_time
                self.process_image(file_path)
    
    def process_image(self, image_path):
        """Process the image and copy result to clipboard with optimizations."""
        try:
            print(f"Processing image: {image_path}")
            
            # Send notification that processing started
            self.send_notification("TexTeller", "Processing LaTeX prediction...", "info")
            
            start_time = time.time()
            
            # Use torch.no_grad() for inference to save memory
            with torch.no_grad():
                prediction = img2latex(
                    model=self.model,
                    tokenizer=self.tokenizer,
                    images=[image_path],
                    device=self.device,
                    out_format="katex",
                    keep_style=False,
                    num_beams=1
                )[0]
            
            inference_time = time.time() - start_time
            
            print(f"Predicted LaTeX: {prediction}")
            print(f"⚡ Inference time: {inference_time:.2f}s")
            
            # Copy to clipboard
            self.copy_to_clipboard(prediction)
            print("Result copied to clipboard!")
            
            # Send success notification with timing info
            self.send_notification("TexTeller", f"LaTeX prediction completed in {inference_time:.2f}s and copied to clipboard!", "success")
            
        except Exception as e:
            print(f"Error processing image: {e}")
            # Send error notification
            self.send_notification("TexTeller", f"Error processing image: {str(e)}", "error")
    
    def send_notification(self, title, message, notification_type="info"):
        """Send desktop notification using notify-send."""
        try:
            # Map notification types to notify-send urgency levels
            urgency_map = {
                "info": "normal",
                "success": "normal", 
                "error": "critical",
                "warning": "normal"
            }
            
            urgency = urgency_map.get(notification_type, "normal")
            
            # Send notification using notify-send
            subprocess.run([
                'notify-send', 
                f'--urgency={urgency}',
                '--app-name=TexTeller',
                title, 
                message
            ], check=True)
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"Warning: Could not send notification. Make sure notify-send is installed.")
        except Exception as e:
            print(f"Warning: Could not send notification: {e}")
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard using system clipboard."""
        try:
            # Try different clipboard methods based on the system
            if sys.platform == "linux":
                # For Linux, try xclip first, then xsel
                try:
                    subprocess.run(['xclip', '-selection', 'clipboard'], input=text, text=True, check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    try:
                        subprocess.run(['xsel', '--clipboard', '--input'], input=text, text=True, check=True)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        print("Warning: Could not copy to clipboard. Install xclip or xsel.")
            elif sys.platform == "darwin":  # macOS
                subprocess.run(['pbcopy'], input=text, text=True, check=True)
            elif sys.platform == "win32":  # Windows
                subprocess.run(['clip'], input=text, text=True, check=True)
            else:
                print(f"Warning: Clipboard not supported on platform {sys.platform}")
        except Exception as e:
            print(f"Warning: Could not copy to clipboard: {e}")


def main():
    """Main function to run the optimized latex predictor daemon."""
    print("🚀 Loading TexTeller model with optimizations...")
    
    # Load model and tokenizer once at startup with optimizations
    try:
        # Use ONNX for better performance with GPU support
        model = load_model(use_onnx=True)
        tokenizer = load_tokenizer()
        device = get_device()
        
        print(f"Model loaded successfully on device: {device}")
        
        # Additional ONNX optimizations
        if ORTModelForVision2Seq is not None and isinstance(model, ORTModelForVision2Seq):
            print("🔥 Applying ONNX runtime optimizations...")
            # Set optimal execution providers
            if device.type == 'cuda':
                print("Using CUDA execution provider with optimizations")
            else:
                print("Using CPU execution provider with optimizations")
        
        # Send startup notification
        try:
            subprocess.run([
                'notify-send', 
                '--urgency=normal',
                '--app-name=TexTeller',
                'TexTeller Optimized Daemon', 
                f'Model loaded with optimizations on {device}. Monitoring /tmp/latexPredict.png'
            ], check=True)
        except:
            pass  # Don't fail if notification doesn't work
            
    except Exception as e:
        print(f"Error loading model: {e}")
        return 1
    
    # Set up file monitoring for the specific file
    target_file = Path("/tmp/latexPredict.png")
    event_handler = OptimizedLatexPredictorHandler(model, tokenizer, device, target_file)
    observer = Observer()
    
    # Monitor the directory containing the target file
    observer.schedule(event_handler, "/tmp", recursive=False)
    
    print(f"Monitoring file: {target_file}")
    print("⚡ Optimized daemon ready - waiting for changes to latexPredict.png...")
    print("Press Ctrl+C to stop.")
    
    try:
        observer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping optimized daemon...")
        observer.stop()
    
    observer.join()
    print("Optimized daemon stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
