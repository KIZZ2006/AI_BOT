import os
import sys
import torch
import numpy as np

# Add local face_detection to path
sys.path.append(os.getcwd())

import face_detection

device = 'cpu'
print(f"Using {device}")

try:
    detector = face_detection.FaceAlignment(face_detection.LandmarksType._2D, 
                                            flip_input=False, device=device)
    print("Detector initialized successfully")
    
    # Dummy image
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    preds = detector.get_detections_for_batch(np.array([img]))
    print("Detection ran successfully")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
