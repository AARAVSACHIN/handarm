
import socket
import time
import sys

# --- CONFIGURATION (Match your hand_tracker_servo.py) ---
ARDUINO_IP = "192.168.1.15"  # CHANGE THIS to your actual Arduino IP
UDP_PORT = 4210

def send_angle(sock, joint_id, angle):
    data = bytes([joint_id, angle])
    print(f"Sending -> Joint:{joint_id} Angle:{angle} to {ARDUINO_IP}")
    sock.sendto(data, (ARDUINO_IP, UDP_PORT))

def main():
    print("--- 4-DOF Robotic Arm Communication Diagnostic ---")
    print(f"Target IP: {ARDUINO_IP} | Port: {UDP_PORT}")
    print("This script will try to move each servo from 90 to 120 and back.")
    print("Press Ctrl+C to stop.")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        while True:
            # Test each of the 4 servos
            for joint_id in range(4):
                print(f"\n--- Testing Servo {joint_id} ---")
                
                # Move to 120 degrees
                send_angle(sock, joint_id, 120)
                time.sleep(1)
                
                # Move back to 90 degrees
                send_angle(sock, joint_id, 90)
                time.sleep(1)
                
            print("\nCycle complete. Restarting in 2 seconds...")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nDiagnostic stopped by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
