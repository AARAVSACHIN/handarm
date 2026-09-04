/**
 * @file arduino_servo.ino
 * @brief Professional Arduino 4-DOF Vertical Robotic Arm (Static Base)
 * @description Controls 3 vertical tilt joints and 1 gripper.
 *              Receives 2-byte commands [JointID, Angle] from Python.
 * 
 * Hardware Setup (Static Base):
 * - Servo 0 (Shoulder Tilt) -> Pin 9
 * - Servo 1 (Elbow Tilt)    -> Pin 10
 * - Servo 2 (Wrist Tilt)    -> Pin 11
 * - Servo 3 (Gripper)       -> Pin 6
 */

#include <Servo.h>

const int NUM_SERVOS = 4;
const int SERVO_PINS[NUM_SERVOS] = {9, 10, 11, 6}; 
const long BAUD_RATE = 115200; // MUST MATCH ESP8266 BRIDGE BAUD

// Joint Limits (Safety Constraints)
// Vertical tilt joints often need careful limits to prevent collision with base
const int JOINT_MINS[NUM_SERVOS] = {30, 0, 0, 0};   // Shoulder, Elbow, Wrist, Gripper
const int JOINT_MAXS[NUM_SERVOS] = {150, 180, 180, 90}; 
const float SMOOTHING_FACTORS[NUM_SERVOS] = {0.1, 0.15, 0.2, 0.25}; // Heavier joints move slower

Servo servos[NUM_SERVOS];
float currentAngles[NUM_SERVOS];
int targetAngles[NUM_SERVOS];

void setup() {
  Serial.begin(BAUD_RATE);
  for (int i = 0; i < NUM_SERVOS; i++) {
    servos[i].attach(SERVO_PINS[i]);
    // Start at a "neutral" upward-facing pose
    int start = (i == 3) ? 0 : 90; 
    currentAngles[i] = start;
    targetAngles[i] = start;
    servos[i].write(start);
  }
  Serial.println("ARDUINO_READY");
}

void loop() {
  while (Serial.available() > 0) {
    int firstByte = Serial.peek();
    
    // Check if the first byte looks like a valid Joint ID (0-3)
    // If not, it might be startup text or noise, so discard it
    if (firstByte < 0 || firstByte >= NUM_SERVOS) {
      Serial.read(); // Discard
      continue;
    }
    
    // If we have at least 2 bytes, read the full command
    if (Serial.available() >= 2) {
      int jointID = Serial.read();
      int angle = Serial.read();
      targetAngles[jointID] = constrain(angle, JOINT_MINS[jointID], JOINT_MAXS[jointID]);
    } else {
      break; // Wait for the second byte to arrive
    }
  }
  
  for (int i = 0; i < NUM_SERVOS; i++) {
    currentAngles[i] = (targetAngles[i] * SMOOTHING_FACTORS[i]) + (currentAngles[i] * (1.0 - SMOOTHING_FACTORS[i]));
    servos[i].write((int)currentAngles[i]);
  }
  delay(15);
}
