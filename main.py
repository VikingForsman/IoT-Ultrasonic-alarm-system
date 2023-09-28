from network import WLAN     # Used for connecting the device to Wifi
import urequests as requests # Used for sending data to ubidots
from machine import Pin      # Used for defining the sensor and actuator pins
import pycom                 # Used for the LED lights
import time                  # Used for measuring time in seconds
import utime                 # Used for measuring time in microseconds

# Pins
button = Pin('P9', mode=Pin.IN, pull=Pin.PULL_UP)
trig = Pin('P10', mode=Pin.OUT)
echo = Pin('P11', mode=Pin.IN)
sound = Pin('P12', mode = Pin.OUT)
time.sleep(2)

# Wifi
wlan = WLAN(mode=WLAN.STA)
wlan.antenna(WLAN.INT_ANT)
wlan.connect("Name here", auth=(WLAN.WPA2, "Password here"), timeout=5000)
while not wlan.isconnected ():
    machine.idle()
print("Connected to Wifi\n")
token = "Token here" # Ubidots token

# Variables
red = 0x7f0000
green = 0x007f00
blue = 0x00007f

# Function that builds the json
def build_json(variable, value):
    try:
        message = {1: "Alarm is offline", 2: "Alarm is online", 3: "Alarm is triggered", 4: "Unauthorized entry"}
        data = {variable: {"value": value, "context" : {"message" : message[value]}}}
        return data
    except:
        return None


# Function that sends the request to the REST API https://ubidots.com/docs/api/
def post_var(device, value):
    try:
        url = "https://industrial.api.ubidots.com/api/v1.6/devices/" + device
        headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
        data = build_json("status", value)
        if data is not None:
            print(data)
            req = requests.post(url=url, headers=headers, json=data)
            return req.json()
        else:
            print("Error, Invalid data!")
            pass
    except:
        print("Error, invalid request!")
        pass


# Function that measure the distance
def measure_distance():
    # Calculate the offset (may change depending on hardware)
    start = utime.ticks_us()
    end = utime.ticks_us()
    offset = utime.ticks_diff(end, start)

    # Emit ultrasonic sound for 10 microseconds
    trig.value(1)
    utime.sleep_us(10)
    trig.value(0)

    # Calculate the difference in time between the sent signal and the echo
    start = utime.ticks_us()
    while not echo():
        pass
    end = utime.ticks_us()
    difference = utime.ticks_diff(end, start) # measuring travel time

    # Return the distance in centimeters
    return ((difference-offset)/2)/29


# Function that active the alarm via a button press
def alarm_activation():
    print("Press the button to activate the alarm...")
    post_var("pycom", 1)
    pycom.rgbled(green)
    while True:
        if button() == 0:
            print("The alarm will be active in 20 seconds!")
            pycom.rgbled(blue)
            time.sleep(20)
            post_var("pycom", 2)
            break
        time.sleep(1)


# Function that can trigger the alarm depending on the ultrasonic sensor
def alarm_execute():
    pycom.rgbled(red)
    print("The alarm is now active!")
    print("Press the button to deactivate the alarm...")

    # Measure the distance initial distance to the door
    distance_initial = measure_distance()
    time.sleep(1)

    # Determine the lower and higher threshold
    Distance_higher_threshold = distance_initial + 5;
    Distance_lower_threshold = distance_initial - 5;

    while True:
        distance = measure_distance()
        print('Deviation:', distance - distance_initial, 'cm')
        utime.sleep(1)

        # Determine if thresholds are crossed or if the button is pressed
        if button() == 0:
            print("The alarm was deactivated with the button...")
            pycom.rgbled(green)
            time.sleep(1)
            return False
        elif distance < Distance_lower_threshold:
            print("The alarm was triggered by the lower threshold...")
            post_var("pycom", 3)
            return True
        elif distance > Distance_higher_threshold:
            print("The alarm was triggered by the higher threshold...")
            post_var("pycom", 3)
            return True


# Function that emit sound from buzzer
def alarm_sound(duration):
    t_end = time.time() + duration
    while time.time() < t_end:
        sound.value(1)
        time.sleep(0.002)
        sound.value(0)
        time.sleep(0.002)


# Function that measure distance and trigger the alarm
def alarm_triggered():
    # check for button press in 20 seconds
    t_end = time.time() + 20
    pycom.rgbled(blue)
    while time.time() < t_end:
        if button() == 0:
            print("The alarm was deactivated with the button...")
            pycom.rgbled(green)
            time.sleep(1)
            return
        time.sleep(1)

    # sound the alarm for 60 seconds
    pycom.rgbled(red)
    post_var("pycom", 4)
    alarm_sound(60)


# Looping through the main behaviors of the system
pycom.heartbeat(False)
while True:
    alarm_activation()
    if alarm_execute():
        alarm_triggered()
