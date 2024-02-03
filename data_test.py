from machine import Pin, I2C, ADC
from neopixel import Neopixel
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
import machine, neopixel
import urequests
import time
import network
import json

# def connect()

# initialize LED
numpix = 30
strip = Neopixel(numpix, 0 , 4, "RGB")
strip.brightness(10)

# initialize potentiometer
adc = ADC(Pin(26))
pot_max = 65535

# initialize data
latitude = 51.04
longitude = -114.07
url = "https://api.open-meteo.com/v1/forecast?latitude=" + str(latitude) + " &longitude=" + str(longitude) + " &hourly=temperature_2m&timezone=auto"
# r = urequests.get(url)
# data = r.json()
f = open('data.json')
data = json.load(f)

max_temp = -100
min_temp = 100
for temp in data['hourly']['temperature_2m']:
    if temp > max_temp:
        max_temp = temp
            
    if temp < min_temp:
        min_temp = temp

temp_diff = max_temp - min_temp

print(max_temp)
print(min_temp)
print(temp_diff)

def show_temp_datetime():
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr(f'Temp: {temp}')
    lcd.move_to(0,1)
    lcd.putstr(f'{date} {date_time}')

cur_option = 0
def menu():
    num_options = 4
    option = round(adc.read_u16() / pot_max * (num_options - 1)) + 1
    
    if option != cur_option:
        if option == 1:
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr(f'>View Temp/Date')
            lcd.move_to(0,1)
            lcd.putstr(f'Change Lat/Long')
        elif option == 2:
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr(f'>Change Lat/Long')
            lcd.move_to(0,1)
            lcd.putstr(f'View Balls')
        elif option == 3:
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr(f'>View Balls')
            lcd.move_to(0,1)
            lcd.putstr(f'Exit')
        elif option == 4:
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr(f'>Exit')
        
    return option
    
def update_data():
    # url = "https://api.open-meteo.com/v1/forecast?latitude=" + str(latitude) + " &longitude=" + str(longitude) + " &hourly=temperature_2m&timezone=auto"
    # r = urequests.get(url)
    # data = r.json()
    
    max_temp = -100
    min_temp = 100
    for temp in data['hourly']['temperature_2m']:
        if temp > max_temp:
            max_temp = temp
            
        if temp < min_temp:
            min_temp = temp

    temp_diff = max_temp - min_temp

# initialize LCD
I2C_ADDR     = 63
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# while True:
#     menu()
#     cur_option = menu()
#     time.sleep(0.1)

offset = 0
while True:
    for i in range(30):
        if offset < (164 - i):
            j = i + offset
        else:
            j = i + offset - 164
            
        scale = (data['hourly']['temperature_2m'][j] - min_temp) / temp_diff
        
        print(scale)
        
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
    
    temp = data['hourly']['temperature_2m'][j]
    date = data['hourly']['time'][j][5:10]
    date_time = data['hourly']['time'][j][11:]
    latitude = round(adc.read_u16() / pot_max * 360 - 180, 2)
    
    strip.show()
    show_temp_datetime()
    
    # print(offset)
    if offset < 163:
        offset += 1
    else:
        offset = 0
        
    time.sleep(0.1)

# We need to close the response so that the Pi Pico does not crash
# r.close()