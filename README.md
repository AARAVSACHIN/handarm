# HandArm — Hand-Gesture Controlled Robotic Arm
 
Control a 4-DOF robotic arm in real time using just your webcam and hand movements. A Python script uses MediaPipe to track your hand, maps finger and wrist positions to servo angles, and streams commands to an Arduino/ESP8266 over Wi-Fi (UDP) or USB serial.
 
## How It Works
 
1. Your webcam feed is processed by MediaPipe's Hand Landmarker model to detect 21 hand landmarks.
2. Key landmark positions are converted into angles for four joints:
   - **Shoulder** — based on wrist height
   - **Elbow** — based on wrist-to-knuckle vertical distance
   - **Wrist** — based on knuckle-to-fingertip vertical distance
   - **Gripper** — based on thumb-to-index pinch distance
3. Angles are smoothed with an exponential moving average (EMA) to avoid jittery servo motion.
4. Commands are sent as 2-byte packets (`joint_id`, `angle`) either over UDP Wi-Fi to an ESP8266/Arduino, or over USB serial.
## Hardware
 
- 4x SG90 servo motors (shoulder, elbow, wrist, gripper)
- Arduino (USB mode) and/or ESP8266 (Wi-Fi mode)
- Webcam
## Files
 
| File | Purpose |
|---|---|
| `hand_tracker_servo.py` | Main script — webcam capture, hand tracking, angle calculation, and command sending |
| `arduino_servo/arduino_servo.ino` | Arduino sketch that receives servo commands over USB serial |
| `esp8266_bridge/esp8266_bridge.ino` | ESP8266 sketch that receives servo commands over Wi-Fi (UDP) |
| `hand_landmarker.task` | MediaPipe hand tracking model (auto-downloaded if missing) |
| `list_ports.py` | Utility to list available USB serial ports |
| `diagnostic_test.py` | Sends a test sweep (90°→120°→90°) to each servo over UDP, for wiring/connectivity checks |
| `test_patch.py` | Compatibility patch/test for using `cvzone.HandTrackingModule` with newer MediaPipe versions |
| `requirements.txt` | Python dependencies |
 
## Setup
 
### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```
 
### 2. Choose your connection mode
Open `hand_tracker_servo.py` and set:
```python
MODE = 'WIFI'   # or 'USB'
```
 
**Wi-Fi mode:**
- Flash `esp8266_bridge/esp8266_bridge.ino` to your ESP8266.
- Update `ARDUINO_IP` in `hand_tracker_servo.py` to match your ESP8266's IP address.
**USB mode:**
- Flash `arduino_servo/arduino_servo.ino` to your Arduino.
- Run `list_ports.py` to find your Arduino's COM port, then update `ARDUINO_PORT` in `hand_tracker_servo.py`.
### 3. Run it
```bash
python hand_tracker_servo.py
```
Press `q` to quit.
 
## Testing & Diagnostics
 
- **Check available serial ports:** `python list_ports.py`
- **Test servo wiring/connectivity (Wi-Fi mode):** `python diagnostic_test.py` — sweeps each of the 4 servos from 90° to 120° and back, one at a time.
## Tuning
 
- `EMA_SMOOTHING` in `hand_tracker_servo.py` (default `0.15`) controls responsiveness vs. stability. Lower = smoother but slower to react; higher = snappier but more jittery.
- `CAMERA_INDEX` — change if you have multiple webcams.
## Notes
 
- The hand tracking model (`hand_landmarker.task`) is downloaded automatically on first run if not already present.
- Only one hand is tracked at a time (`num_hands=1`).
