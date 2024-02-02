from machine import Pin, I2C, ADC
from neopixel import Neopixel
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
import machine, neopixel
import urequests
import time
import network
import json
    
# initialize LCD
I2C_ADDR     = 63
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# initialize LED
numpix = 30
strip = Neopixel(numpix, 0 , 4, "RGB")
strip.brightness(10)

# initialize potentiometer
adc = ADC(Pin(26))

latitude = 51.04
longitude = -114.07
url = "https://api.open-meteo.com/v1/forecast?latitude=" + str(latitude) + " &longitude=" + str(longitude) + " &hourly=temperature_2m&timezone=auto"
# r = urequests.get(url)
    
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

# Potentiometer Stats
pot_max = 65535

def show_lcd():
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr(f'Temp: {data['hourly']['temperature_2m'][j]}')
    lcd.move_to(0,1)
    lcd.putstr(f'Latitude: {latitude}')

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
    
    show_lcd()
    
    latitude = round(adc.read_u16() / pot_max * 360 - 180, 2)
    print(f'latitude: {latitude}')
    
    # print(offset)
    if offset < 163:
        offset += 1
    else:
        offset = 0
        
    time.sleep(0.5)

# We need to close the response so that the Pi Pico does not crash
# r.close()