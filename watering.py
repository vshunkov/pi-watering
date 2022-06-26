#!/usr/bin/env python3
import requests, time
import RPi.GPIO as GPIO
# import bot_token, bot_chatID from vars.py
from vars import *

sensor_statuses = ['True', 'False']
sensors = [3,5,7,11,23]
relays = [12, 16, 18, 22]
# [0]ZoneID, [1]Relay pin, [2]Sensors list, [3]Watering duration(min), [4]Check sensor status
ZONE1 = [1, 12, [3,5,7], 30, True]
ZONE2 = [2, 16, [11], 3, True]
ZONE3 = [3, 18, [23], 3, True]
ZONE4 = [4, 22, [11], 3, False]

def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()

def sensor_status(sensors):
    count = 0
    for i in sensors:
        if sensor_statuses[GPIO.input(i)] == 'True':
            count += 1
    return count/len(sensors) > 0.5

def sensor_message(sensors):
    status = ""
    for i in sensors:
        status = status + "Sensor"+ str(i) +": "+ str(sensor_statuses[GPIO.input(i)]) +"\n"
    return status

def watering(data):
    message = "==========\nZone"+ str(data[0]) +" watering:\nSensors initial status:\n"+ sensor_message(data[2])
    if data[4] and sensor_status(data[2]): 
        message = message + "Skipping watering"
    else:
        GPIO.output(data[1], False)
        time.sleep(data[3]*60)
        GPIO.output(data[1], True)
        message = message + "\nSensors current status:\n"+ sensor_message(data[2]) +"Duration: "+ str(data[3]) +" min\n=========="

    telegram_bot_sendtext(message)

try:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(relays, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(sensors, GPIO.IN)
    watering(ZONE1)
    watering(ZONE2)
    watering(ZONE3)
    watering(ZONE4)
finally:
    GPIO.cleanup
