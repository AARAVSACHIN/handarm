import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import serial
import time
import numpy as np
import math
import socket
import os
import urllib.request

# --- CONFIGURATION ---
MODE = 'WIFI' 
ARDUINO_IP = "192.168.1.15" # Replace with your real IP
UDP_PORT = 4210
ARDUINO_PORT = 'COM3' 
BAUD_RATE = 115200
CAMERA_INDEX = 0

# --- STABILITY CONFIGURATION ---
EMA_SMOOTHING = 0.15      # 0.0 to 1.0 (Lower = smoother but slower, Higher = snappier but jittery)
# 0.15 is very stable for robotic arms.
prev_angles = [90, 90, 90, 0] # Initial pose memory for smoothing

# --- MEDIAPIPE NEW API SETUP ---
MODEL_PATH = "hand_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

def download_model():
    if not os.path.exists(MODEL_PATH):
        print(f"Downloading hand tracking model ({MODEL_PATH})... please wait.")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Download complete.")

class HandDetectorNew:
    def __init__(self):
        download_model()
        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.5,
            running_mode=vision.RunningMode.IMAGE
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def findHands(self, frame):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        detection_result = self.detector.detect(mp_image)
        
        hands_list = []
        if detection_result.hand_landmarks:
            for idx, landmarks in enumerate(detection_result.hand_landmarks):
                h, w, _ = frame.shape
                lmList = []
                for lm in landmarks:
                    lmList.append([int(lm.x * w), int(lm.y * h), lm.z])
                
                hands_list.append({"lmList": lmList})
                
                # Draw landmarks manually
                for lm in lmList:
                    cv2.circle(frame, (lm[0], lm[1]), 3, (0, 255, 0), cv2.FILLED)
        
        return hands_list, frame

def apply_ema(new_angle, idx):
    global prev_angles
    smoothed = int((new_angle * EMA_SMOOTHING) + (prev_angles[idx] * (1.0 - EMA_SMOOTHING)))
    prev_angles[idx] = smoothed
    return smoothed

def connect_arduino_usb(port):
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=2)
        print(f"USB Mode: Connected to Arduino on {port}")
        time.sleep(2)
        return ser
    except:
        return None

def main():
    # Initialize Detector
    detector = HandDetectorNew()
    
    # Setup Connection
    conn = None
    if MODE == 'WIFI':
        conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"WiFi Mode: Sending data to {ARDUINO_IP}:{UDP_PORT}")
    else:
        conn = connect_arduino_usb(ARDUINO_PORT)
    
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    print("--- Professional Stabilized Vertical Arm Control ---")
    print(f"Smoothing Factor: {EMA_SMOOTHING}")
    print("Press 'q' to quit.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success: break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hands, frame = detector.findHands(rgb_frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if hands:
            hand = hands[0]
            lmList = hand["lmList"]
            h, w, _ = frame.shape

            # Extract Key Points
            wrist_y = lmList[0][1] / h
            mcp_y = lmList[9][1] / h
            tip_y = lmList[12][1] / h
            
            def get_dist_px(p1, p2):
                return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

            # --- CALCULATE RAW TARGETS ---
            raw_shoulder = int(np.interp(wrist_y, [0.2, 0.8], [150, 30]))
            raw_elbow = int(np.interp(wrist_y - mcp_y, [-0.2, 0.2], [45, 135]))
            raw_wrist = int(np.interp(mcp_y - tip_y, [-0.15, 0.15], [45, 135]))
            
            hand_scale = get_dist_px(lmList[0], lmList[9])
            pinch_dist = get_dist_px(lmList[4], lmList[8])
            raw_gripper = int(np.interp(pinch_dist / hand_scale, [0.2, 0.8], [0, 90]))

            # --- APPLY SMOOTHING (EMA) ---
            shoulder_angle = apply_ema(raw_shoulder, 0)
            elbow_angle = apply_ema(raw_elbow, 1)
            wrist_angle = apply_ema(raw_wrist, 2)
            gripper_angle = apply_ema(raw_gripper, 3)

            # --- SEND COMMANDS ---
            commands = [(0, shoulder_angle), (1, elbow_angle), (2, wrist_angle), (3, gripper_angle)]
            
            for joint_id, angle in commands:
                data = bytes([joint_id, angle])
                if MODE == 'WIFI':
                    try:
                        conn.sendto(data, (ARDUINO_IP, UDP_PORT))
                    except: pass
                elif MODE == 'USB' and conn:
                    conn.write(data)
            
            # Feedback on screen
            cv2.putText(frame, f"S:{shoulder_angle} E:{elbow_angle} W:{wrist_angle} G:{gripper_angle}", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Debug info in console
            if time.time() % 0.5 < 0.05:
                print(f"Stabilized Angles -> S:{shoulder_angle} E:{elbow_angle} W:{wrist_angle} G:{gripper_angle}")

        cv2.imshow('FaceForge: Stabilized Control', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    if MODE == 'USB' and conn: conn.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
