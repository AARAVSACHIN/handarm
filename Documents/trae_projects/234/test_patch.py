
import cv2
import mediapipe as mp
import mediapipe.python.solutions.hands as mp_hands
import mediapipe.python.solutions.drawing_utils as mp_draw

# Patch
class S: pass
mp.solutions = S()
mp.solutions.hands = mp_hands
mp.solutions.drawing_utils = mp_draw

from cvzone.HandTrackingModule import HandDetector
try:
    detector = HandDetector(detectionCon=0.8, maxHands=1)
    print("PATCH_SUCCESS")
except Exception as e:
    print(f"PATCH_FAILED: {e}")
