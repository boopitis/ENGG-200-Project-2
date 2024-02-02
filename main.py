from machine import Pin
from neopixel import Neopixel
import machine, neopixel
import urequests
import time
import network
import json

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

# r = urequests.get("https://api.open-meteo.com/v1/forecast?latitude=51.04&longitude=-114.07&hourly=temperature_2m&timezone=auto")
    
f = open('data.json')

data = json.load(f)

# Most APIs will return JSON, which acts like a Python dictionary

data_dict = {}

for index, date_time in enumerate(data['hourly']['time']):
    data_dict[date_time] = data['hourly']['temperature_2m'][index]

print(data_dict)

max_temp = -100
max_temp_index = -1
min_temp = 100
min_temp_index = -1
for index, temp in enumerate(data['hourly']['temperature_2m']):
    if temp > max_temp:
        max_temp = temp
        max_temp_index = index
        
    if temp < min_temp:
        min_temp = temp
        min_temp_index = index

print(max_temp)
print(min_temp)

temp_diff = max_temp - min_temp

print(temp_diff)

numpix = 30
strip = Neopixel(numpix, 0 , 0, "RGB")

offset = 0
while True:
    for i in range(30):
        if offset < (164 - i):
            j = i + offset
        else:
            j = i + offset - 164
            
        scale = (data['hourly']['temperature_2m'][j] + abs(min_temp)) / temp_diff
            
        if scale <= (1/5):
            strip.set_pixel(i, (0, 255 * (1 - scale), 255))
        elif scale <= (2/5):
            strip.set_pixel(i, (255 * scale, 0, 255))
        elif scale <= (3/5):
            strip.set_pixel(i, (255, 0, 255 * (1 - scale)))
        elif scale <= (4/5):
            strip.set_pixel(i, (255, 255 * scale, 0))
        else:
            strip.set_pixel(i, (255 * (1 - scale), 255, 0))
    
    strip.show()
    time.sleep(0.1)
    print(offset)
    if offset < 163:
        offset += 1
    else:
        offset = 0

# We need to close the response so that the Pi Pico does not crash
# r.close()