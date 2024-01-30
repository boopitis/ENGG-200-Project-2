from machine import Pin
import machine, neopixel
import urequests
import time
import network

ssid = 'airuc-guest' # This should be ‘airuc-guest’ on campus Wi-Fi
password = ''

def connect():
    # Connect to WLAN
    # Connect function from https://projects.raspberrypi.org/en/projects/get-started-pico-w/2
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid) # Remove password if using airuc-guest
    
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        time.sleep(1)
try:
    connect()
except KeyboardInterrupt:
    machine.reset()
    
print('Connected. End of code.')

r = urequests.get("https://api.dictionaryapi.dev/api/v2/entries/en/university")

data = r.json()

# Most APIs will return JSON, which acts like a Python dictionary

for all in data:
    print(all)

# for i, v in enumerate(data['hourly']['time']):
#    print(f'{i}. {v}')

# We need to close the response so that the Pi Pico does not crash
r.close()