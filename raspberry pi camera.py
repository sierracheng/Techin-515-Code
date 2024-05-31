import time
from datetime import datetime
import subprocess
import pyrebase
import board
import busio
import adafruit_vl53l0x

# Firebase configuration
config = {
    "apiKey": "AIzaSyBwvWX_Wfx_EBMLq96k6AgQKH3Xp0wLFgs",
    "authDomain": "farmbeats-ceeb5.firebaseapp.com",
    "databaseURL": "https://farmbepathats-ceeb5-default-rtdb.firebaseio.com",
    "projectId": "farmbeats-ceeb5",
    "storageBucket": "farmbeats-ceeb5.appspot.com",
    "messagingSenderId": "543508894183",
    "appId": "1:543508894183:web:01b179f0b97a1f95016d42"
}

# Initialize Pyrebase
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()

# Initialize I2C and VL53L0X
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_vl53l0x.VL53L0X(i2c)

# Function to take photo and upload it using libcamera
def capture_and_upload():
    now = datetime.now()
    filename = f'photo_{now.strftime("%Y%m%d_%H%M%S")}.jpg'
    distance_filename = f'distance_{now.strftime("%Y%m%d_%H%M%S")}.txt'
    
    # Using libcamera-jpeg to capture the image with specified resolution
    command = f'libcamera-jpeg -o {filename} --width 3280 --height 2464'
    subprocess.run(command, shell=True)
    print(f"Captured {filename}")
    
    # Measure distance
    distance = sensor.range
    print(f"Measured distance: {distance} mm")

    # Save distance data to a text file
    with open(distance_filename, 'w') as f:
        f.write(f"Distance: {distance} mm")
    
    # Upload photo
    storage.child(f"images/{filename}").put(filename)
    storage.child(f"backup/{filename}").put(filename)
    print(f"Uploaded {filename}")

    # Upload distance data
    storage.child(f"distances/{distance_filename}").put(distance_filename)
    print(f"Uploaded distance data to {distance_filename}")

    # Clean up files locally
    subprocess.run(f'rm {filename} {distance_filename}', shell=True)

try:
    while True:
        capture_and_upload()
        time.sleep(3600)  # Wait for one hour
except KeyboardInterrupt:
    print("Stopped by User")
except Exception as e:
    print(f"An error occurred: {e}")
