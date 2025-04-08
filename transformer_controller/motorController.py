import RPi.GPIO as GPIO

class MotorController:
    def __init__(self, RA, RB, LA, LB):
        self.RA = RA
        self.RB = RB
        self.LA = LA
        self.LB = LB
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RA, GPIO.OUT)
        GPIO.setup(RB, GPIO.OUT)
        GPIO.setup(LA, GPIO.OUT)
        GPIO.setup(LB, GPIO.OUT)
        
    def forward(self):
        GPIO.output(self.RA, True)
        GPIO.output(self.RB, False)
        GPIO.output(self.LA, True)
        GPIO.output(self.LB, False) 
               
    def backward(self):
        GPIO.output(self.RA, False)
        GPIO.output(self.RB, True)
        GPIO.output(self.LA, False)
        GPIO.output(self.LB, True)
        
    def turnRight(self):
        GPIO.output(self.RA, False)
        GPIO.output(self.RB, True)
        GPIO.output(self.LA, True)
        GPIO.output(self.LB, False)
        
    def turnLeft(self):
        GPIO.output(self.RA, True)
        GPIO.output(self.RB, False)
        GPIO.output(self.LA, False)
        GPIO.output(self.LB, True)
        
    def stop(self):
        GPIO.output(self.RA, False)
        GPIO.output(self.RB, False)
        GPIO.output(self.LA, False)
        GPIO.output(self.LB, False)
        
    def clean(self):
        GPIO.cleanup(self.RA)
        GPIO.cleanup(self.RB)
        GPIO.cleanup(self.LB)
        GPIO.cleanup(self.LB)