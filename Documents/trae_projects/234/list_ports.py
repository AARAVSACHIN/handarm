import serial.tools.list_ports

def list_serial_ports():
    """List all available serial ports on the system."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No serial ports found. Please ensure your Arduino is plugged in.")
        return
    
    print("Available serial ports:")
    for port in ports:
        print(f"- {port.device}: {port.description}")

if __name__ == "__main__":
    list_serial_ports()
