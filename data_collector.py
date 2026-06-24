import cv2
import mediapipe as mp
import numpy as np
import os
import time

# MediaPipe new Tasks API imports
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Setup the MediaPipe HandLandmarker
base_options = python.BaseOptions(model_asset_path=r'd:\Image Project\hand_landmarker.task')
options = vision.HandLandmarkerOptions(base_options=base_options,
                                       num_hands=1)
detector = vision.HandLandmarker.create_from_options(options)

# Manually define hand connections for drawing without legacy mp.solutions
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index finger
    (5, 9), (9, 10), (10, 11), (11, 12),   # Middle finger
    (9, 13), (13, 14), (14, 15), (15, 16), # Ring finger
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20) # Pinky
]

# Create necessary directories for database and reference images
DATA_DIR = r'd:\Image Project\database'
REF_DIR = r'd:\Image Project\reference_images'
for dir_path in [DATA_DIR, REF_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

# Canvas dimensions from user requirements
CANVAS_WIDTH = 1680
CANVAS_HEIGHT = 1050
QUAD_WIDTH = CANVAS_WIDTH // 2  # 840
QUAD_HEIGHT = CANVAS_HEIGHT // 2  # 525

cap = cv2.VideoCapture(0)

current_alphabet = 'A'
save_count = 0

# Check saved count for initial alphabet
save_dir = os.path.join(DATA_DIR, current_alphabet)
if os.path.exists(save_dir):
    save_count = len(os.listdir(save_dir))

def get_reference_image(alphabet):
    img_path = os.path.join(REF_DIR, f"{alphabet}.jpg")
    if os.path.exists(img_path):
        img = cv2.imread(img_path)
        if img is not None:
            img = cv2.resize(img, (QUAD_WIDTH, QUAD_HEIGHT))
            return img
    img = np.zeros((QUAD_HEIGHT, QUAD_WIDTH, 3), dtype=np.uint8)
    img[:] = (30, 30, 30) # Dark gray background
    cv2.putText(img, f"No Ref Image for '{alphabet}'", (120, QUAD_HEIGHT//2 - 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
    cv2.putText(img, f"Place {alphabet}.jpg in", (180, QUAD_HEIGHT//2 + 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
    cv2.putText(img, f"'reference_images' folder", (160, QUAD_HEIGHT//2 + 70), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
    return img

print("Starting Sign Language Data Collector...")
print("Window size will be 1680x1050.")

cv2.namedWindow("Sign Language System", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Sign Language System", CANVAS_WIDTH, CANVAS_HEIGHT)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame from camera.")
        break
    
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (QUAD_WIDTH, QUAD_HEIGHT))
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    detection_result = detector.detect(mp_image)
    
    black_bg = np.zeros((QUAD_HEIGHT, QUAD_WIDTH, 3), dtype=np.uint8)
    cropped_img_to_save = None

    if len(detection_result.hand_landmarks) > 0:
        hand_landmarks = detection_result.hand_landmarks[0]
        h, w, _ = frame.shape
        
        # Convert landmarks to pixel coordinates
        pixels = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]
        
        # Draw on both regular frame and black background
        for img_target in [frame, black_bg]:
            # Draw Connections
            for connection in HAND_CONNECTIONS:
                p1 = pixels[connection[0]]
                p2 = pixels[connection[1]]
                cv2.line(img_target, p1, p2, (0, 255, 0), 3)
            # Draw points
            for point in pixels:
                cv2.circle(img_target, point, 4, (0, 0, 255), -1)

        x_coords = [p[0] for p in pixels]
        y_coords = [p[1] for p in pixels]
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        pad = 50
        y_min = max(0, y_min - pad)
        y_max = min(h, y_max + pad)
        x_min = max(0, x_min - pad)
        x_max = min(w, x_max + pad)
        
        cropped_img_to_save = black_bg[y_min:y_max, x_min:x_max]

    ref_img = get_reference_image(current_alphabet)
    
    output_bg = np.zeros((QUAD_HEIGHT, QUAD_WIDTH, 3), dtype=np.uint8)
    output_bg[:] = (40, 40, 40)
    
    cv2.putText(output_bg, "Sign Language Collector", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255, 255, 255), 4)
    cv2.putText(output_bg, f"Current Alphabet: {current_alphabet}", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
    cv2.putText(output_bg, f"Images Saved: {save_count}", (50, 260), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 3)
    
    cv2.putText(output_bg, "Controls:", (50, 360), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    cv2.putText(output_bg, "'a'-'z' : Change alphabet", (80, 420), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200, 200, 200), 2)
    cv2.putText(output_bg, "'s' : Save current hand sign", (80, 460), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200, 200, 200), 2)
    cv2.putText(output_bg, "'q' : Quit", (80, 500), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200, 200, 200), 2)

    canvas = np.zeros((CANVAS_HEIGHT, CANVAS_WIDTH, 3), dtype=np.uint8)
    canvas[0:QUAD_HEIGHT, 0:QUAD_WIDTH] = frame
    canvas[0:QUAD_HEIGHT, QUAD_WIDTH:CANVAS_WIDTH] = black_bg
    canvas[QUAD_HEIGHT:CANVAS_HEIGHT, 0:QUAD_WIDTH] = ref_img
    canvas[QUAD_HEIGHT:CANVAS_HEIGHT, QUAD_WIDTH:CANVAS_WIDTH] = output_bg
    
    thickness = 5
    cv2.line(canvas, (QUAD_WIDTH, 0), (QUAD_WIDTH, CANVAS_HEIGHT), (255, 255, 255), thickness)
    cv2.line(canvas, (0, QUAD_HEIGHT), (CANVAS_WIDTH, QUAD_HEIGHT), (255, 255, 255), thickness)
    
    cv2.putText(canvas, "1. Webcam Capture", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(canvas, "2. Hand Sign Structure (Black BG)", (QUAD_WIDTH + 20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    cv2.putText(canvas, "3. Reference Image", (20, QUAD_HEIGHT + 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow("Sign Language System", canvas)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key >= ord('a') and key <= ord('z'):
        current_alphabet = chr(key).upper()
        save_dir = os.path.join(DATA_DIR, current_alphabet)
        if os.path.exists(save_dir):
            save_count = len(os.listdir(save_dir))
        else:
            save_count = 0
            
    elif key == ord('s'):
        save_dir = os.path.join(DATA_DIR, current_alphabet)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        if cropped_img_to_save is not None and cropped_img_to_save.size > 0:
            h, w, _ = cropped_img_to_save.shape
            img_size = 300
            img_bg = np.zeros((img_size, img_size, 3), np.uint8)
            aspect_ratio = h / max(w, 1) # prevent division by zero
            
            if aspect_ratio > 1:
                k = img_size / h
                w_cal = int(np.ceil(k * w))
                img_resize = cv2.resize(cropped_img_to_save, (w_cal, img_size))
                w_gap = int(np.ceil((img_size - w_cal) / 2))
                img_bg[:, w_gap:w_cal + w_gap] = img_resize
            else:
                k = img_size / w
                h_cal = int(np.ceil(k * h))
                img_resize = cv2.resize(cropped_img_to_save, (img_size, h_cal))
                h_gap = int(np.ceil((img_size - h_cal) / 2))
                img_bg[h_gap:h_cal + h_gap, :] = img_resize
                
            img_name = os.path.join(save_dir, f"{current_alphabet}_{int(time.time()*1000)}.jpg")
            cv2.imwrite(img_name, img_bg)
            save_count += 1
            print(f"Saved {img_name}")

cap.release()
cv2.destroyAllWindows()
