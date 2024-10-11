import RPi.GPIO as GPIO
import time
import pyrebase

# Pyrebase configuration
config = {
  "apiKey": "YOUR_API_KEY",
  "authDomain": "YOUR_AUTH_DOMAIN",
  "databaseURL": "YOUR_DATABASE_URL",
  "projectId": "YOUR_PROJECT_ID",
  "storageBucket": "YOUR_STORAGE_BUCKET",
  "messagingSenderId": "YOUR_MESSAGING_SENDER_ID",
  "appId": "YOUR_APP_ID",
  "measurementId": "YOUR_MEASUREMENT_ID"
}

# Initialize Pyrebase
firebase = pyrebase.initialize_app(config)
db = firebase.database()

# Motion sensor pin
pir_pin = 17

# Ultrasonic sensor pins
ultrasonic_trigger_pin = 26
ultrasonic_echo_pin = 19

# Buzzer pin
buzzer_pin = 13

# Keypad GPIO pins
L1 = 18
L2 = 23
L3 = 24
L4 = 25

C1 = 12
C2 = 16
C3 = 20
C4 = 21

# LED pin
led_pin = 6

# DC motor GPIO pin
motor_pin = 4

# Initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Motion sensor setup
GPIO.setup(pir_pin, GPIO.IN)

# Buzzer setup
GPIO.setup(buzzer_pin, GPIO.OUT)
GPIO.output(buzzer_pin, GPIO.LOW)

# Keypad setup
GPIO.setup(L1, GPIO.OUT)
GPIO.setup(L2, GPIO.OUT)
GPIO.setup(L3, GPIO.OUT)
GPIO.setup(L4, GPIO.OUT)

GPIO.setup(C1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(C4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# LED setup
GPIO.setup(led_pin, GPIO.OUT)
GPIO.output(led_pin, GPIO.LOW)  # Initially turn off the LED

# Ultrasonic sensor setup
GPIO.setup(ultrasonic_trigger_pin, GPIO.OUT)
GPIO.setup(ultrasonic_echo_pin, GPIO.IN)

# DC motor setup
GPIO.setup(motor_pin, GPIO.OUT)
motor = GPIO.PWM(motor_pin, 70)  # 50 Hz
motor.start(0)  # Initially stop the motor

# The readLine function implements the procedure discussed in the article
def readLine(line, characters):
    GPIO.output(line, GPIO.HIGH)
    key = None
    if GPIO.input(C1) == GPIO.HIGH:
        key = characters[0]
    elif GPIO.input(C2) == GPIO.HIGH:
        key = characters[1]
    elif GPIO.input(C3) == GPIO.HIGH:
        key = characters[2]
    elif GPIO.input(C4) == GPIO.HIGH:
        key = characters[3]
    GPIO.output(line, GPIO.LOW)
    return key

# Function to sound the alarm
def sound_alarm():
    GPIO.output(buzzer_pin, GPIO.HIGH)
    GPIO.output(led_pin, GPIO.HIGH)  # Turn on the LED
    print("Alarm activated!")

# Function to stop the alarm
def stop_alarm():
    GPIO.output(buzzer_pin, GPIO.LOW)
    GPIO.output(led_pin, GPIO.LOW)  # Turn off the LED
    print("Alarm stopped!")

# Function to start the motor
def start_motor():
    motor.ChangeDutyCycle(70)  # Set the duty cycle to 50%
    print("Doors now locked!")

# Function to stop the motor
def stop_motor():
    motor.ChangeDutyCycle(0)  # Set the duty cycle to 0%
    print("Doors unlocked! Police are on the way!")

# Function to measure distance using ultrasonic sensor
def measure_distance():
    GPIO.output(ultrasonic_trigger_pin, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(ultrasonic_trigger_pin, GPIO.LOW)

    pulse_start = time.time()
    pulse_end = time.time()

    while GPIO.input(ultrasonic_echo_pin) == 0:
        pulse_start = time.time()

    while GPIO.input(ultrasonic_echo_pin) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 34300 / 2
    return round(distance, 2)

try:
    print("Security System")
    print("Initializing...")
    time.sleep(2)
    print("Ready")
    print("Monitoring...")

    is_alarm_active = False
    pin_entered = ""
    ultrasonic_data = {"distance": 0}
    motion_data = {"status": "inactive"}
    alarm_stopped = False
    doors_unlocked = False

    while True:
        pir_status = GPIO.input(pir_pin)
        distance = measure_distance()

        if pir_status == GPIO.HIGH or distance < 20:
            if not is_alarm_active:
                print("Intruder Detected!")
                sound_alarm()
                is_alarm_active = True
                pin_entered = ""
                start_motor()
                db.child("alarm").set("active")  # Update alarm status in Firebase
                db.child("pin_attempts").set(0)  # Reset pin attempts in Firebase
            motion_data["status"] = "detected"
        else:
            if pin_entered == "0000#" and not alarm_stopped:
                stop_alarm()
                is_alarm_active = False
                alarm_stopped = True
                db.child("alarm").set("inactive")  # Update alarm status in Firebase

            if len(pin_entered) >= 5 and not doors_unlocked:
                print("Incorrect PIN")
                pin_entered = ""
                # Increment pin attempts in Firebase
                pin_attempts = db.child("pin_attempts").get().val()
                db.child("pin_attempts").set(pin_attempts + 1)

        ultrasonic_data["distance"] = distance
        db.child("ultrasonic").set(ultrasonic_data)  # Update ultrasonic sensor data in Firebase
        db.child("motion").set(motion_data)  # Update motion sensor data in Firebase

        key = readLine(L1, ["1", "2", "3", "A"])
        if key:
            pin_entered += key
            print(key, end="", flush=True)
        key = readLine(L2, ["4", "5", "6", "B"])
        if key:
            pin_entered += key
            print(key, end="", flush=True)
        key = readLine(L3, ["7", "8", "9", "C"])
        if key:
            pin_entered += key
            print(key, end="", flush=True)
        key = readLine(L4, ["*", "0", "#", "D"])
        if key:
            pin_entered += key
            print(key, end="", flush=True)

        if pin_entered == "0000#":
            if not doors_unlocked:
                stop_motor()
                doors_unlocked = True
                print("Doors Unlocked")

        time.sleep(0.1)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
