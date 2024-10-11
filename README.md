# Intrusion Detection System With Sensors and Firebase Integration

This Python script uses a Raspberry Pi with sensors and integrates with Firebase for real-time monitoring of a security system. The script can detect motion using a PIR sensor, measure distances using an ultrasonic sensor, and interact with a keypad, LED, buzzer, and motor. It stores the data in Firebase. When the alarm is triggered and active for more than 5 seconds, the script displays a message simulating a call to 911.

## Dependencies
- Python 3.7
- Pyrebase (Python wrapper for the Firebase API)
- RPi.GPIO (Python module to control Raspberry Pi GPIO channels)

## Instructions
1. Ensure you have Python 3.7 installed on your Raspberry Pi.

2. Install the necessary Python libraries by running the following commands:
    ```bash
    pip install pyrebase
    pip install RPi.GPIO
    ```

3. Clone this repository or download the script file to your Raspberry Pi.

4. Modify the `config` dictionary in the Python script with your Firebase project's credentials. These can be found in your Firebase console.

5. Wire your PIR motion sensor, ultrasonic sensor, keypad, LED, buzzer, and motor to the appropriate GPIO pins on your Raspberry Pi as described in the script. Ensure everything is connected properly to avoid any hardware damage or incorrect readings.

6. Run the script by navigating to the directory where the script is located and executing the following command:
    ```bash
    python3 script.py
    ```

7. The script will start monitoring for motion and distances. When motion is detected or if an object is detected within a certain distance range, the alarm will be triggered. The alarm can be stopped by entering the correct pin on the keypad. If the alarm stays active for more than 5 seconds, a message simulating a call to 911 will be displayed.

8. To stop the script, press `Ctrl + C`.
