#!/usr/bin/env python3
"""
Benchmark script to compare standard vs optimized daemon performance.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
import numpy as np
import cv2

import torch
from texteller.api import load_model, load_tokenizer, img2latex
from texteller.utils import get_device


def create_test_images(num_images=5):
    """Create multiple test images for benchmarking."""
    test_images = []
    
    for i in range(num_images):
        # Create a test image with mathematical content
        img = np.ones((200, 400, 3), dtype=np.uint8) * 255
        
        # Add different mathematical expressions
        expressions = [
            'E = mc^2',
            'x^2 + y^2 = r^2',
            '\\int_0^\\infty e^{-x} dx = 1',
            '\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}',
            '\\nabla \\times \\vec{E} = -\\frac{\\partial \\vec{B}}{\\partial t}'
        ]
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, expressions[i], (20, 100), font, 0.7, (0, 0, 0), 2)
        
        # Save image
        img_path = Path(f"/tmp/test_image_{i}.png")
        cv2.imwrite(str(img_path), img)
        test_images.append(str(img_path))
    
    return test_images


def benchmark_standard_model():
    """Benchmark the standard model."""
    print("🔍 Benchmarking Standard Model...")
    print("-" * 40)
    
    # Load standard model
    start_time = time.time()
    model = load_model(use_onnx=True)
    tokenizer = load_tokenizer()
    device = get_device()
    load_time = time.time() - start_time
    
    print(f"Model load time: {load_time:.2f}s")
    print(f"Device: {device}")
    
    # Create test images
    test_images = create_test_images(3)
    
    # Benchmark inference
    inference_times = []
    for i, img_path in enumerate(test_images):
        start_time = time.time()
        
        with torch.no_grad():
            prediction = img2latex(
                model=model,
                tokenizer=tokenizer,
                images=[img_path],
                device=device,
                out_format="katex",
                keep_style=False,
                num_beams=1
            )[0]
        
        inference_time = time.time() - start_time
        inference_times.append(inference_time)
        
        print(f"Image {i+1} inference time: {inference_time:.2f}s")
        print(f"Prediction: {prediction[:50]}...")
    
    avg_inference_time = sum(inference_times) / len(inference_times)
    print(f"Average inference time: {avg_inference_time:.2f}s")
    
    # Cleanup
    for img_path in test_images:
        os.remove(img_path)
    
    return load_time, avg_inference_time


def benchmark_optimized_model():
    """Benchmark the optimized model."""
    print("\n⚡ Benchmarking Optimized Model...")
    print("-" * 40)
    
    # Load optimized model
    start_time = time.time()
    model = load_model(use_onnx=True)
    tokenizer = load_tokenizer()
    device = get_device()
    
    # Apply optimizations
    import torch
    if hasattr(torch, 'backends'):
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False
    
    if device.type == 'cpu':
        torch.set_num_threads(min(4, os.cpu_count() or 1))
    
    # Compile model if possible
    if hasattr(torch, 'compile') and not isinstance(model, type):
        try:
            print("🔥 Compiling model...")
            model = torch.compile(model, mode="reduce-overhead")
            print("✅ Model compiled!")
        except Exception as e:
            print(f"⚠️  Compilation failed: {e}")
    
    load_time = time.time() - start_time
    
    print(f"Model load time: {load_time:.2f}s")
    print(f"Device: {device}")
    
    # Warm up
    print("🔥 Warming up model...")
    dummy_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    with torch.no_grad():
        _ = img2latex(
            model=model,
            tokenizer=tokenizer,
            images=[dummy_image],
            device=device,
            out_format="katex",
            keep_style=False,
            num_beams=1
        )
    print("✅ Warmup completed!")
    
    # Create test images
    test_images = create_test_images(3)
    
    # Benchmark inference
    inference_times = []
    for i, img_path in enumerate(test_images):
        start_time = time.time()
        
        with torch.no_grad():
            prediction = img2latex(
                model=model,
                tokenizer=tokenizer,
                images=[img_path],
                device=device,
                out_format="katex",
                keep_style=False,
                num_beams=1
            )[0]
        
        inference_time = time.time() - start_time
        inference_times.append(inference_time)
        
        print(f"Image {i+1} inference time: {inference_time:.2f}s")
        print(f"Prediction: {prediction[:50]}...")
    
    avg_inference_time = sum(inference_times) / len(inference_times)
    print(f"Average inference time: {avg_inference_time:.2f}s")
    
    # Cleanup
    for img_path in test_images:
        os.remove(img_path)
    
    return load_time, avg_inference_time


def main():
    """Main benchmark function."""
    print("🚀 TexTeller Performance Benchmark")
    print("=" * 50)
    
    try:
        # Benchmark standard model
        std_load_time, std_inference_time = benchmark_standard_model()
        
        # Benchmark optimized model
        opt_load_time, opt_inference_time = benchmark_optimized_model()
        
        # Compare results
        print("\n📊 Performance Comparison")
        print("=" * 50)
        print(f"Load Time:")
        print(f"  Standard:  {std_load_time:.2f}s")
        print(f"  Optimized: {opt_load_time:.2f}s")
        print(f"  Speedup:   {std_load_time/opt_load_time:.2f}x")
        
        print(f"\nInference Time:")
        print(f"  Standard:  {std_inference_time:.2f}s")
        print(f"  Optimized: {opt_inference_time:.2f}s")
        print(f"  Speedup:   {std_inference_time/opt_inference_time:.2f}x")
        
        print(f"\nOverall Performance:")
        total_std = std_load_time + std_inference_time
        total_opt = opt_load_time + opt_inference_time
        print(f"  Standard Total:  {total_std:.2f}s")
        print(f"  Optimized Total: {total_opt:.2f}s")
        print(f"  Overall Speedup: {total_std/total_opt:.2f}x")
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
