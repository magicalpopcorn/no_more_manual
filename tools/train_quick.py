#!/usr/bin/env python3
"""
Quick YOLO Training Script

A simplified script for quick training with the ds_37 dataset.
Use this for testing or when you want fewer configuration options.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from ultralytics import YOLO

def quick_train():
    """Quick training with minimal configuration"""
    
    # Paths
    dataset_path = project_root / "assests" / "dataset" / "ds_37" / "data.yaml"
    pretrained_model = project_root / "assests" / "yolo_models" / "2000_25.pt"
    
    print(f"Dataset: {dataset_path}")
    print(f"Pre-trained model: {pretrained_model}")
    
    # Load model
    model = YOLO(str(pretrained_model))
    
    # Quick training
    results = model.train(
        data=str(dataset_path),
        epochs=50,              # Fewer epochs for quick training
        batch=8,                # Smaller batch size
        imgsz=640,
        patience=10,
        project=str(project_root / "runs" / "train"),
        name='ds_37_quick',
        exist_ok=True,
        verbose=True
    )
    
    print("Training completed!")
    return results

if __name__ == "__main__":
    quick_train()
