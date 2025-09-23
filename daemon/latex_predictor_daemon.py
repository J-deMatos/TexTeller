#!/usr/bin/env python3
"""
High-level script for TexTeller that loads the model once and monitors a file for changes.
When /tmp/latexPredict.png changes, it makes a prediction and copies the result to clipboard.
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


class LatexPredictorHandler(FileSystemEventHandler):
    """File system event handler for monitoring latexPredict.png changes."""
    
    def __init__(self, model, tokenizer, device, target_file_path):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        # Normalize to absolute path for reliable event matching
        self.target_file_path = os.path.abspath(str(target_file_path))
        self.last_modified = 0
        
    def on_modified(self, event):
        """Handle file modification events."""
        self._handle_file_event(event, "modified")
    
    def on_created(self, event):
        """Handle file creation events."""
        self._handle_file_event(event, "created")
    
    def on_moved(self, event):
        """Handle file move/rename events."""
        self._handle_file_event(event, "moved")
    
    def _handle_file_event(self, event, event_type):
        """Handle any file event that might affect our target file."""
        if event.is_directory:
            return
        
        # Some apps (e.g., gnome-screenshot) write a temp file and then move it
        # into place. For move events we need to check the destination path.
        src_path = os.path.abspath(getattr(event, "src_path", ""))
        dest_path = os.path.abspath(getattr(event, "dest_path", src_path))

        # Determine the relevant path for this event
        candidate_path = dest_path if dest_path else src_path

        # Only process if it's exactly our target file
        if candidate_path == self.target_file_path:
            # Debounce using mtime to avoid duplicate processing bursts
            try:
                current_time = os.path.getmtime(candidate_path)
            except FileNotFoundError:
                # In rare cases, rapid replace can briefly make the file missing; skip
                return
            if current_time > self.last_modified + 1:  # 1 second debounce
                self.last_modified = current_time
                self.process_image(candidate_path)
    
    def process_image(self, image_path):
        """Process the image and copy result to clipboard."""
        try:
            print(f"Processing image: {image_path}")
            
            # Make prediction
            prediction = img2latex(
                model=self.model,
                tokenizer=self.tokenizer,
                images=[image_path],
                device=self.device,
                out_format="katex",
                keep_style=False,
                num_beams=1
            )[0]
            
            print(f"Predicted LaTeX: {prediction}")
            
            # Copy to clipboard
            self.copy_to_clipboard(prediction)
            print("Result copied to clipboard!")
            
            # Send success notification
            self.send_notification("TexTeller", "LaTeX prediction completed and copied to clipboard!", "success")
            
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
    """Main function to run the latex predictor daemon."""
    print("Loading TexTeller model (PyTorch backend)...")
    
    # Load model and tokenizer once at startup
    try:
        # Use standard PyTorch model for correctness (optimize later if needed)
        model = load_model(use_onnx=False)
        tokenizer = load_tokenizer()
        device = get_device()
        print(f"Model loaded successfully on device: {device}")
        
        # Send startup notification
        try:
            subprocess.run([
                'notify-send', 
                '--urgency=normal',
                '--app-name=TexTeller',
                'TexTeller Daemon', 
                f'Model loaded on {device}. Monitoring /tmp/latexPredict.png'
            ], check=True)
        except:
            pass  # Don't fail if notification doesn't work
    except Exception as e:
        print(f"Error loading model: {e}")
        return 1
    
    # Set up file monitoring for the specific file
    target_file = Path("/tmp/latexPredict.png")
    event_handler = LatexPredictorHandler(model, tokenizer, device, target_file)
    observer = Observer()
    
    # Monitor the directory containing the target file
    observer.schedule(event_handler, "/tmp", recursive=False)
    
    print(f"Monitoring file: {target_file}")
    print("Waiting for changes to latexPredict.png...")
    print("Press Ctrl+C to stop.")
    
    try:
        observer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping daemon...")
        observer.stop()
    
    observer.join()
    print("Daemon stopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
