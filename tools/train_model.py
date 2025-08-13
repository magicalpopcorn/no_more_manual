#!/usr/bin/env python3
"""
YOLO Model Training Script

This script trains a YOLO model using the ds_37 dataset with transfer learning
from an existing pre-trained model (2000_25.pt).
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import torch
from ultralytics import YOLO


def train_model():
    """Train YOLO model with the new dataset"""

    # Paths
    dataset_path = project_root / "assests" / "dataset" / "ds_37" / "data.yaml"
    pretrained_model = project_root / "assests" / "yolo_models" / "2000_25.pt"
    output_dir = project_root / "runs" / "train"

    print(f"Dataset path: {dataset_path}")
    print(f"Pre-trained model: {pretrained_model}")
    print(f"Output directory: {output_dir}")

    # Check if files exist
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

    if not pretrained_model.exists():
        raise FileNotFoundError(f"Pre-trained model not found: {pretrained_model}")

    # Load the pre-trained model
    print(f"Loading pre-trained model: {pretrained_model}")
    model = YOLO(str(pretrained_model))

    # Print model info
    print("\nModel Info:")
    print(f"Model size: {model.model}")

    # Check if CUDA is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Training on device: {device}")

    # Training parameters
    training_args = {
        "data": str(dataset_path),
        "epochs": 50,  # Reduced from 100 - good balance for transfer learning
        "batch": 16,  # Batch size (adjust based on GPU memory)
        "imgsz": 640,  # Image size
        "patience": 15,  # Early stopping patience (reduced from 20)
        "save": True,  # Save checkpoints
        "save_period": 10,  # Save checkpoint every N epochs
        "cache": False,  # Cache images for faster training (use if you have enough RAM)
        "device": device,  # Training device
        "workers": 4,  # Number of worker threads
        "project": str(output_dir),  # Project directory
        "name": "ds_37_retrain",  # Run name
        "exist_ok": True,  # Overwrite existing project/name
        "pretrained": True,  # Use pretrained weights
        "optimizer": "auto",  # Optimizer (auto, SGD, Adam, AdamW, NAdam, RAdam, RMSProp)
        "verbose": True,  # Verbose output
        "seed": 42,  # Random seed for reproducibility
        "deterministic": True,  # Deterministic training
        "single_cls": False,  # Multi-class training
        "rect": False,  # Rectangular training
        "cos_lr": False,  # Cosine learning rate scheduler
        "close_mosaic": 10,  # Disable mosaic augmentation for last N epochs
        "resume": False,  # Resume training from last checkpoint
        "amp": True,  # Automatic Mixed Precision training
        "fraction": 1.0,  # Dataset fraction to use
        "profile": False,  # Profile ONNX and TensorRT speeds
        "freeze": None,  # Freeze layers: backbone=10, first3=0:3, etc.
        "lr0": 0.01,  # Initial learning rate
        "lrf": 0.01,  # Final learning rate factor
        "momentum": 0.937,  # SGD momentum/Adam beta1
        "weight_decay": 0.0005,  # Optimizer weight decay
        "warmup_epochs": 3.0,  # Warmup epochs
        "warmup_momentum": 0.8,  # Warmup initial momentum
        "warmup_bias_lr": 0.1,  # Warmup initial bias learning rate
        "box": 7.5,  # Box loss gain
        "cls": 0.5,  # Class loss gain
        "dfl": 1.5,  # DFL loss gain
        "pose": 12.0,  # Pose loss gain (pose models only)
        "kobj": 2.0,  # Keypoint objective loss gain (pose models only)
        "label_smoothing": 0.0,  # Label smoothing
        "nbs": 64,  # Nominal batch size
        "hsv_h": 0.015,  # Image HSV-Hue augmentation (fraction)
        "hsv_s": 0.7,  # Image HSV-Saturation augmentation (fraction)
        "hsv_v": 0.4,  # Image HSV-Value augmentation (fraction)
        "degrees": 0.0,  # Image rotation (+/- deg)
        "translate": 0.1,  # Image translation (+/- fraction)
        "scale": 0.5,  # Image scale (+/- gain)
        "shear": 0.0,  # Image shear (+/- deg)
        "perspective": 0.0,  # Image perspective (+/- fraction), range 0-0.001
        "flipud": 0.0,  # Image flip up-down (probability)
        "fliplr": 0.5,  # Image flip left-right (probability)
        "mosaic": 1.0,  # Image mosaic (probability)
        "mixup": 0.0,  # Image mixup (probability)
        "copy_paste": 0.0,  # Segment copy-paste (probability)
        "auto_augment": "randaugment",  # Auto augmentation policy for classification (randaugment, autoaugment, augmix)
        "erasing": 0.4,  # Random erasing probability for classification
        "crop_fraction": 1.0,  # Image crop fraction for classification
    }

    print(f"\nStarting training with the following parameters:")
    for key, value in training_args.items():
        print(f"  {key}: {value}")

    # Start training
    print(f"\n{'='*50}")
    print("STARTING TRAINING")
    print(f"{'='*50}")

    try:
        results = model.train(**training_args)

        print(f"\n{'='*50}")
        print("TRAINING COMPLETED SUCCESSFULLY!")
        print(f"{'='*50}")

        # Print results summary
        if results:
            print(f"Training results: {results}")

        # Print location of best model
        best_model_path = output_dir / "ds_37_retrain" / "weights" / "best.pt"
        print(f"\nBest model saved at: {best_model_path}")

        if best_model_path.exists():
            print("You can copy this model to the yolo_models directory:")
            target_path = project_root / "assests" / "yolo_models" / "ds_37_retrained.pt"
            print(f"cp '{best_model_path}' '{target_path}'")

        return True

    except Exception as e:
        print(f"\n{'='*50}")
        print(f"TRAINING FAILED: {e}")
        print(f"{'='*50}")
        return False


def main():
    """Main function"""
    print("YOLO Model Training Script")
    print("=" * 50)

    try:
        success = train_model()
        if success:
            print("\nTraining completed successfully!")
            sys.exit(0)
        else:
            print("\nTraining failed!")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
