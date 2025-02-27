import board
import busio
import time
import random
import rotaryio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer
import pwmio
from adafruit_motor import servo
from adafruit_ina219 import INA219

from adafruit_ht16k33 import segments

Version = "Version 1.0"

class CableReleaseController:
    
    TIME_SET=1
    DELAY_SET=2
    TAKING_PICTURE=3
    
    MAX_SHUTTER = 60
    MIN_SHUTTER = 1
    
    MAX_DELAY = 60
    MIN_DELAY = 0
    
    MAX_SERVO_ANGLE=107
    MIN_SERVO_ANGLE=20
    CENTRE_SERVO_ANGLE=50
    
    MAX_CURRENT=100

    def __init__(self, i2c_sda,i2c_scl,
                 encoder_a,encoder_b,encoder_button,
                 time_button
                 ):
        # Make i2c connection
        self.i2c = busio.I2C(i2c_scl, i2c_sda)
        self.ina = INA219(self.i2c)
        # Make display
        self.display = segments.Seg14x4(self.i2c)
        self.display_text('Hi  ')
        time.sleep(2)
        # Make encoder
        self.encoder= rotaryio.IncrementalEncoder(encoder_a, encoder_b)
        self.enc_pos=self.encoder.position
        # Make encoder button
        tmp_pin = DigitalInOut(encoder_button)
        tmp_pin.pull = Pull.UP
        self.encoder_button = Debouncer(tmp_pin,interval=0.01)
        # Make time button
        tmp_pin = DigitalInOut(time_button)
        tmp_pin.pull = Pull.UP
        self.time_button = Debouncer(tmp_pin,interval=0.01)
        self.state=self.TIME_SET
        self.delay_time=0
        self.shutter_time=1.0
        self.display_times()
        pwm_servo = pwmio.PWMOut(board.GP4, duty_cycle=2 ** 15, frequency=50)
        self.servo = servo.Servo(
            pwm_servo, min_pulse=500, max_pulse=2200
        )  # tune pulse for specific servo
        self.servo_home()
    
    def servo_home(self):
        self.servo.angle=self.MIN_SERVO_ANGLE
        self.show_current()
        
    def servo_trigger(self):
        self.servo.angle=self.MAX_SERVO_ANGLE
        self.show_current()
    
    def display_text(self, text):
        self.display.fill(0)
        self.display.print(text)
        
    def scroll_text(self,text):
        self.display.marquee(text, delay=0.25, loop=False)
        
    def display_values(self,shutter,delay):
        d=f"{delay:2}{shutter:2}"
        self.display_text(d)
        
    def display_times(self):
        self.display_values(self.shutter_time,self.delay_time)
        
    def show_current(self):
        bus_voltage = self.ina.bus_voltage  # Voltage across the load (V)
        current = self.ina.current  # Current in mA
        power = self.ina.power  # Power in mW
        shunt_voltage = self.ina.shunt_voltage  # Voltage drop across the shunt resistor (mV)

        # Print readings
        print(f"Bus Voltage: {bus_voltage:.2f} V")
        print(f"Current: {current:.2f} mA")
        print(f"Power: {power:.2f} mW")
        print(f"Shunt Voltage: {shunt_voltage:.2f} mV")
        

    def limit_test(self,start,delta,max_current):
        self.servo.angle = start
        result = start
        while True:
            self.servo.angle = result+delta
            time.sleep(1.5)
            current=self.ina.current
            print(f"   Current:{current} Angle:{result}")
            if self.ina.current >= max_current:
                self.servo.angle = result
                print(f"Result:{result}")
                return result
            time.sleep(0.2)
            result = result + delta
        
    def set_limits(self):
        self.servo.angle = self.CENTRE_SERVO_ANGLE
        # do the inner limit first
        self.MIN_SERVO_ANGLE = self.limit_test(self.CENTRE_SERVO_ANGLE,-1,self.MAX_CURRENT)
        self.MAX_SERVO_ANGLE = self.limit_test(self.CENTRE_SERVO_ANGLE,1,self.MAX_CURRENT)
        
    def update(self):
        
        self.time_button.update()
        
        if self.time_button.fell:
            print("Taking a picture")
            self.display_text("****")
            time.sleep(0.2)
            # Start with the delay
            dt = self.delay_time
            st = self.shutter_time
            while(dt>0):
                self.display_values(st,dt)
                time.sleep(1)
                dt=dt-1
            # now do the exposure
            self.display_values(st,dt)
            self.servo_trigger()
            while(st>0):
                self.display_values(st,0)
                time.sleep(1)
                st=st-1
            self.servo_home()
            self.display_times()
            return
       
        self.encoder_button.update()

        if self.encoder_button.fell:
            self.state=self.DELAY_SET

        if self.encoder_button.rose:
            self.state=self.TIME_SET
            
        new_pos = self.encoder.position
        if new_pos == self.enc_pos:
            return
        
        # encoder turned
        delta=new_pos-self.enc_pos
        self.enc_pos=new_pos
        
        if self.state==self.TIME_SET:
            self.shutter_time = self.shutter_time+delta
            if self.shutter_time < self.MIN_SHUTTER:
                self.shutter_time = self.MIN_SHUTTER
            if self.shutter_time > self.MAX_SHUTTER:
                self.shutter_time = self.MAX_SHUTTER
                
        if self.state==self.DELAY_SET:
            self.delay_time = self.delay_time+delta
            if self.delay_time < self.MIN_DELAY:
                self.delay_time = self.MIN_DELAY
            if self.delay_time > self.MAX_DELAY:
                self.delay_time = self.MAX_DELAY
                
        self.display_times()        
        

    def servo_test(self):
        while True:
            print("tick")
            self.servo_home()
            time.sleep(1)
            self.servo_trigger()
            time.sleep(1)
            
    def button_test(self):
        print("Testing the button")
        while True:
            self.time_button.update()
            if self.time_button.fell:
                print("button pressed")
            if self.time_button.rose:
                print("button released")
            
            
            
    def run(self):
        print("Cable Release Rob Miles (www.robmiles.com) " + Version)
        while True:
            self.update()
            time.sleep(0.01)

    

cable = CableReleaseController(i2c_sda=board.GP0, i2c_scl=board.GP1,
                 encoder_a=board.GP8,encoder_b=board.GP9,encoder_button=board.GP22,
                 time_button=board.GP16
                 )
#cable.button_test()
#cable.servo_test()
cable.run()


