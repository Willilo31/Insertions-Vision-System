import Jetson.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

Green = 11
Red = 13
Alarm = 15
Motor = 16
Light = 18

GPIO.setup(Green, GPIO.OUT)
GPIO.output(Green, False)

GPIO.setup(Light, GPIO.OUT)
GPIO.output(Light, False)

GPIO.setup(Red, GPIO.OUT)
GPIO.output(Red, True)

GPIO.setup(Alarm, GPIO.OUT)
GPIO.output(Alarm, True)

GPIO.setup(Motor, GPIO.OUT)
GPIO.output(Motor, True)

GPIO.cleanup()



