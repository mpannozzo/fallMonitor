import serial
import csv

# --- CONFIGURATION ---
# Change 'COM3' to match your Pico's actual port (e.g., 'COM4', 'COM5')
COM_PORT = 'COM3'  
BAUD_RATE = 115200 
FILE_NAME = 'Test6-16.csv'

try:
    # Open the physical hardware port
    ser = serial.Serial(COM_PORT, BAUD_RATE)
    print(f"Connected to {COM_PORT}. Recording data...")

    # Create and open the CSV file automatically
    with open(FILE_NAME, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write our column headers
        writer.writerow(['Accel_X', 'Accel_Y', 'Accel_Z', 'Fall_Indicator'])

        # Infinite loop catching the 50Hz data
        while True:
            if ser.in_waiting > 0:
                # Read line, convert bytes to text, strip whitespace
                line = ser.readline().decode('utf-8').strip()
                
                # Filter out any bootup text words, only capture comma data
                if "," in line:
                    data = line.split(',')
                    writer.writerow(data)

except KeyboardInterrupt:
    print("\nRecording stopped successfully. Your file has been saved locally!")

except serial.SerialException as e:
    print(f"\nSerial Port Error: {e}")
    print("Make sure your Pico is plugged in and all other serial monitors are CLOSED.")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port safely released.")