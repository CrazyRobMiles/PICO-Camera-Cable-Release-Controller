# PICO-Camera-Cable-Release-Controller
![camera](images/controller.jpg)

Use a PICO and a servo to control a cable release for an old-school mechanical camera. 

## You will need
* Raspberry Pi PICO - any version will do If you want to add WiFi or Bluetooth remote control use a PICO W. 
* A four character alphanumeric display with an HT16K33 backpack. Search for "ht16k33 14 segment led". Make sure that you get the 14 segment device as this can display text. Some have different colours for each pair of digit. These work well because one side will be the exposure time and the other will be the self-timer delay. 
* A large push button (preferably one with a nice colour)
* A rotary encoder (search for KY-040 encoder)
* An MG995 servo
* CJMCU-219 Bi-Directional DC Current Sensor (INA219)
* A three and a two AA battery holder
* A DC-DC converter to reduce the 7.5v battery to 5v to power the PICO
* A power switch. I used latching push buttons which fit into a 12mm diam hole
* A camera cable release. The longest you can find. However, if your camera has a selfo

## Usage

Connect the cable release to your camera. When the controller is powered on it will select a self timer delay of 0 seconds and an exposure of 1 second. Turn the rotary encoder to increase or decrease exposure. Push the encoder down and turn it to adjust the self-timer duration. Press the button to take a picture. The display will count down the self timer and then fire the shutter.

## Circuit

![circuit](images/circuit.png)
If you don't want the power monitoring feature you can leave off the current sensor.

## Software

The software runs in Circuit Python. You can download it for your device [here](https://circuitpython.org/downloads). 
You can find all the software in the python folder. Copy all the files in the Python folder onto the root of your PICO once you have installed Circuit Python on it. The supplied librarie files are for Circuit Python Version 9. If you want to use a different version you may have to install different libraries. 

## Case

You can find the print files for the case top and bottom. The actuator components are a remix of [this design](https://www.thingiverse.com/thing:3170748).  

Have Fun

Rob Miles