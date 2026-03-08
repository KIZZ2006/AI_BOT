import cv2
import mediapipe as mp
import numpy as np
import os
import math
import json
import shutil
from rembg import remove, new_session
from PIL import Image

# Robust MediaPipe Import
try:
    import mediapipe.python.solutions.face_mesh as mp_face_mesh_sol
    mp_face_mesh = mp_face_mesh_sol
except (ImportError, AttributeError):
    try:
        import mediapipe as mp
        mp_face_mesh = mp.solutions.face_mesh
    except:
        mp_face_mesh = None
        print("⚠️ Warning: MediaPipe face mesh initialization failed.")

face_mesh = None
if mp_face_mesh:
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1)

def get_path(rel_path):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root, rel_path.replace("/", os.sep))

def remove_bg(input_path, output_path):
    print(f"[BG_REMOVE] Attempting background removal for {input_path}...")
    
    try:
        from rembg import new_session
        providers = ['CPUExecutionProvider']
        if os.environ.get('COLAB_GPU', '0') == '1' or 'CUDA_VISIBLE_DEVICES' in os.environ:
             print("   -> T4 GPU Detected. Using CUDA for Background Removal...")
             providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
        else:
             print("   -> Using CPU for Background Removal...")
        
        session = new_session(providers=providers)
    except Exception as e:
        print(f"   -> Session init failed: {e}. Using default.")
        session = None

    with open(input_path, 'rb') as i:
        input_data = i.read()
        try:
            output_data = remove(input_data, session=session)
        except Exception as e:
            print(f"   -> Removal Error: {e}. Trying default session...")
            output_data = remove(input_data)
            
        with open(output_path, 'wb') as o:
            o.write(output_data)

def humanize_avatar(host_name="Daniel", duration=12, fps=25):
    import random
    # Mapping to Multiple High-Quality Variants
    HOSTS = {
        "Daniel": ["images/daniel_pro.png", "images/daniel_v2.png", "images/main.png"],
        "Sarah": ["images/sarah_pro.png", "images/sarah_v1.png", "images/sarah_v2.png", "images/avatar2.jpeg"]
    }
    
    # Pick a random variant for this run
    variant_list = HOSTS.get(host_name, HOSTS["Daniel"])
    input_image_path_rel = random.choice(variant_list)
    input_image_path = get_path(input_image_path_rel)
    
    # Per-Variant Caching: Each avatar style gets its own pre-rendered loop
    variant_id = os.path.basename(input_image_path_rel).split(".")[0]
    cache_dir = get_path("cache")
    os.makedirs(cache_dir, exist_ok=True)
    master_loop_path = os.path.join(cache_dir, f"{host_name}_{variant_id}_loop.mp4")
    target_intermediate = get_path("advanced_pipeline/intermediate/input_face_916.mp4")
    
    # SYSTEM 1: USE CACHE IF IT EXISTS
    if os.path.exists(master_loop_path) and duration != 99: 
        print(f"📦 Quality Cache Hit: Using {variant_id} for {host_name}")
        os.makedirs(os.path.dirname(target_intermediate), exist_ok=True)
        shutil.copy(master_loop_path, target_intermediate)
        return

    # SYSTEM 2: GENERATE MASTER LOOP (ONE TIME COST)
    print(f"[DNA] Generating {duration}s Master Loop for {host_name}...")
    print("   This is a one-time process. Future runs will be INSTANT.")
    
    temp_no_bg = get_path("temp/host_no_bg.png")
    os.makedirs(os.path.dirname(temp_no_bg), exist_ok=True)
    remove_bg(input_image_path, temp_no_bg)
    
    img = cv2.imread(temp_no_bg, cv2.IMREAD_UNCHANGED)
    h, w = img.shape[:2]
    canvas_h, canvas_w = 1920, 1080
    
    results = None
    landmarks = None
    if face_mesh:
        results = face_mesh.process(cv2.cvtColor(cv2.imread(input_image_path), cv2.COLOR_BGR2RGB))
        landmarks = results.multi_face_landmarks[0] if results.multi_face_landmarks else None
    else:
        print("⚠️ Warning: Skipping blink logic (MediaPipe missing).")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(master_loop_path, fourcc, fps, (canvas_w, canvas_h))

    LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
    RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]

    total_frames = duration * fps
    for i in range(total_frames):
        # PERFORMANCE DNA: Human logic instead of math
        # 1. Natural Sway: Slow, organic breathing/shifting
        base_sway = math.sin(i * 0.05) * 4 # 4px Sway
        
        # 2. Processing Nods (Thinking movements)
        # Random bursts of tiny nods to simulate engagement
        nod_burst = math.sin(i * 0.8) * 1.5 if (i // 50) % 3 == 0 else 0
        
        # 3. Shoulder Breathing
        # Subtle expansion of the chest/shoulders
        shoulder_scale = 1.0 + (math.sin(i * 0.08) * 0.005)

        # 4. Eye Saccades (Cognition)
        # Random darts during pauses
        import random
        eye_dart_x = random.randint(-2, 2) if i % 45 == 0 else 0
        eye_dart_y = random.randint(-1, 1) if i % 45 == 0 else 0

        frame_canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
        frame_canvas[:] = (255, 0, 255) # Magenta Screen
        
        # Combine movements
        final_shift_x = base_sway + eye_dart_x
        final_shift_y = nod_burst + eye_dart_y
        final_angle = math.sin(i * 0.02) * 1.0 # 1 degree tilt

        # Apply transformations to the host image
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, final_angle, shoulder_scale)
        M[0, 2] += final_shift_x
        M[1, 2] += final_shift_y
        
        moved_host = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))

        blink_cycle = int(fps * 3.8)
        blink_frame = i % blink_cycle
        is_blinking = blink_frame < 4 
        
        if is_blinking and landmarks:
            overlay = moved_host.copy()
            for eye_indices in [LEFT_EYE, RIGHT_EYE]:
                points = []
                for idx in eye_indices:
                    pt = landmarks.landmark[idx]
                    px, py = pt.x * w, pt.y * h
                    nx = M[0, 0] * px + M[0, 1] * py + M[0, 2]
                    ny = M[1, 0] * px + M[1, 1] * py + M[1, 2]
                    points.append((int(nx), int(ny)))
                if len(points) > 0:
                    cv2.fillPoly(overlay, [np.array(points)], (10, 10, 10, 255))
            cv2.addWeighted(overlay, 0.7, moved_host, 0.3, 0, moved_host)

        # PREMIUM FRAMING: 95% height, shifted for 'Viral Zone' logic
        host_h, host_w = moved_host.shape[:2]
        target_h = int(canvas_h * 0.95) # Larger for more presence
        target_w = int(host_w * (target_h / host_h))
        
        # Prevent horizontal overflow
        if target_w > canvas_w:
            target_w = canvas_w
            target_h = int(host_h * (target_w / host_w))
            
        resized_host = cv2.resize(moved_host, (target_w, target_h))
        x_offset = (canvas_w - target_w) // 2
        
        # BOTTOM ANCHOR: Sit the host naturally at the bottom
        y_offset = canvas_h - target_h
        
        if resized_host.shape[2] == 4:
            # OPTIMIZED VECTOR BLENDING (NumPy)
            alpha_3d = (resized_host[:, :, 3] / 255.0)[:, :, np.newaxis]
            frame_canvas[y_offset:y_offset+target_h, x_offset:x_offset+target_w, :] = \
                (alpha_3d * resized_host[:, :, :3] + (1 - alpha_3d) * frame_canvas[y_offset:y_offset+target_h, x_offset:x_offset+target_w, :]).astype(np.uint8)
        else:
            frame_canvas[y_offset:y_offset+target_h, x_offset:x_offset+target_w, :] = resized_host[:, :, :3]
            
        out.write(frame_canvas)
        if i % 200 == 0:
            print(f"   Rendering Master Loop: {i}/{total_frames} frames...")

    out.release()
    print(f"✅ Success: Master Loop cached at {master_loop_path}")
    shutil.copy(master_loop_path, target_intermediate)

if __name__ == "__main__":
    host = "Daniel"
    meta_path = get_path("outputs/metadata.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r") as f:
                data = json.load(f)
                host = data.get("host", "Daniel")
        except: pass
    humanize_avatar(host_name=host)
