import Jetson.GPIO as GPIO
import time 

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

Green = 11
Red = 13
Alarm = 15
Motor = 16

GPIO.setup(Green, GPIO.OUT)
GPIO.output(Green, True)

GPIO.setup(Motor, GPIO.OUT)
GPIO.output(Motor, True)

GPIO.setup(Red, GPIO.OUT)
GPIO.output(Red, False)

GPIO.setup(Alarm, GPIO.OUT)
GPIO.output(Alarm, False)

time.sleep(5)
GPIO.output(Red, True)
GPIO.output(Alarm, True)
GPIO.output(Motor, False)

time.sleep(3.6)

GPIO.output(Motor, True)
GPIO.output(Green, False)

GPIO.cleanup()