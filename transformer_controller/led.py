import RPi.GPIO as GPIO

class LED:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        
    def on(self):
        GPIO.output(self.pin, True)
        
    def off (self):
        GPIO.output(self.pin, False)
        
    def clean(self):
        GPIO.cleanup(self.pin)