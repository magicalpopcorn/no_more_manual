# YOLO Model Training Guide

## Dataset Information
- **Dataset**: ds_37 (6 classes)
- **Classes**: gem-z-out, march_attacking, march_farming, march_idle, march_marching, march_returning
- **Pre-trained model**: 2000_25.pt
- **Location**: `assests/dataset/ds_37/`

## Training Options

### Option 1: Full Training (Recommended)
```bash
cd tools
python train_model.py
```

This script includes:
- Complete training configuration
- 100 epochs with early stopping
- Comprehensive data augmentation
- Automatic device detection (GPU/CPU)
- Detailed logging and monitoring

### Option 2: Quick Training (For Testing)
```bash
cd tools
python train_quick.py
```

This script includes:
- Simplified configuration
- 50 epochs
- Faster training for testing purposes

## Training Parameters (train_model.py)

### Key Settings:
- **Epochs**: 100 (with early stopping patience=20)
- **Batch Size**: 16 (adjust based on GPU memory)
- **Image Size**: 640x640
- **Learning Rate**: 0.01 (initial)
- **Device**: Auto-detected (CUDA if available)

### GPU Memory Considerations:
- **16GB+ GPU**: batch=16 (default)
- **8-12GB GPU**: batch=8
- **4-8GB GPU**: batch=4
- **CPU only**: batch=2

To adjust batch size, edit the `batch` parameter in the training script.

## Output

### Training Results:
- **Location**: `runs/train/ds_37_retrain/`
- **Best Model**: `runs/train/ds_37_retrain/weights/best.pt`
- **Last Model**: `runs/train/ds_37_retrain/weights/last.pt`

### After Training:
Copy the best model to your models directory:
```bash
cp runs/train/ds_37_retrain/weights/best.pt assests/yolo_models/ds_37_retrained.pt
```

## Monitoring Training

### Real-time Monitoring:
The training script will output:
- Loss values (box, cls, dfl)
- Validation metrics (mAP50, mAP50-95)
- Learning rate and epoch progress

### TensorBoard (Optional):
```bash
pip install tensorboard
tensorboard --logdir runs/train
```

## Resume Training

If training is interrupted, you can resume:
```python
# In the training script, change:
'resume': True,  # Set to True
```

## Model Validation

After training, test your model:
```python
from ultralytics import YOLO

# Load your trained model
model = YOLO('assests/yolo_models/ds_37_retrained.pt')

# Validate on test set
results = model.val(data='assests/dataset/ds_37/data.yaml')

# Run inference on an image
results = model('path/to/test/image.jpg')
```

## Troubleshooting

### Common Issues:

1. **Out of Memory Error**:
   - Reduce batch size
   - Reduce image size (imgsz=416 instead of 640)

2. **CUDA Not Available**:
   - Training will automatically fall back to CPU
   - CPU training is much slower

3. **Dataset Path Issues**:
   - Ensure data.yaml paths are correct
   - Use absolute paths if needed

4. **Permission Errors**:
   - Make sure you have write access to the runs/ directory

### Performance Tips:

1. **Faster Training**:
   - Use GPU if available
   - Increase batch size (if memory allows)
   - Set cache=True (if you have enough RAM)

2. **Better Results**:
   - Train for more epochs
   - Use data augmentation
   - Experiment with learning rates

## Next Steps

After training:
1. Evaluate model performance on validation set
2. Test on real game screenshots
3. Compare with previous model (2000_25.pt)
4. Update your game automation script to use the new model

## Model Integration

To use the new model in your ROK automation:
```python
# In your gather_gem.py or similar file
model_path = "assests/yolo_models/ds_37_retrained.pt"
model = YOLO(model_path)
```
