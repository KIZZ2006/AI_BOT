import cv2
import os
import sys
import torch
from gfpgan import GFPGANer

def enhance_video(input_path, output_path, upscale=1):
    print(f"✨ [Enhancing] Sharpening video: {input_path}")
    
    # Initialize GFPGAN
    # model_path = 'gfpgan/experiments/pretrained_models/GFPGANv1.4.pth'
    model_path = os.path.join('gfpgan_core_repo', 'experiments', 'pretrained_models', 'GFPGANv1.4.pth')
    
    # Check if CPU or GPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"   Using device: {device}")
    
    restorer = GFPGANer(
        model_path=model_path,
        upscale=upscale,
        arch='clean',
        channel_multiplier=2,
        bg_upsampler=None # We only want to fix the face to prevent melting background
    )

    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"   Processing {total_frames} frames...")

    count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # GFPGAN restore
        # has_face: whether has face in the image
        # restored_faces: a list of restored faces
        # restored_img: the restored image
        _, _, restored_img = restorer.enhance(frame, has_aligned=False, only_center_face=False, paste_back=True)
        
        out.write(restored_img)
        count += 1
        if count % 20 == 0:
            print(f"   Enhanced {count}/{total_frames} frames...")

    cap.release()
    out.release()
    print(f"✅ Enhancement Complete! Saved to: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        # Debugging
        # enhance_video('outputs/final_test_wav2lip.mp4', 'outputs/final_test_hd.mp4')
        pass
    else:
        enhance_video(sys.argv[1], sys.argv[2])
