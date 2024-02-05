from machine import Pin
import time

button = Pin(14, Pin.IN, Pin.PULL_UP)

while True:
    if button.value() == 0:
        print('yo')
    time.sleep(0.1)