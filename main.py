from machine import Pin, I2C, ADC
from neopixel import Neopixel
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
import neopixel
import urequests
import time
import network
import json
import sys

# initialize LCD
I2C_ADDR     = 63
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# initialize LED strip
numpix = 11
strip = Neopixel(numpix, 0 , 4, "RGB")
brightness = 255
strip.brightness(brightness)

# initialize potentiometer
adc = ADC(Pin(26))
pot_max = 65535

# initialize button
button = Pin(14, Pin.IN, Pin.PULL_UP)
button_pressed = False

def connect(ssid, password):
    # Connect to WLAN
    # Connect function from https://projects.raspberrypi.org/en/projects/get-started-pico-w/2
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password) # ADD PASSWORD IF NEEDED
    
    count = 1
    offset = 0
    while wlan.isconnected() == False:
        print(f'Waiting for connection to {ssid}')
        lcd.clear()
        lcd.move_to(0,0)
        lcd.putstr(f'Connecting..({count})')
        lcd.move_to(0,1)
        lcd.putstr(f'{ssid}')
        
        for i in list(range(numpix))[::-1]:
            if offset < (11 - i):
                j = i + offset
            else:
                j = i + offset - 11
                    
            scale = (j+1)/11
            
            if scale <= (1/5):
                strip.set_pixel(i, (0, 255 * (1 - scale * 5), 255))
            elif scale <= (2/5):
                strip.set_pixel(i, (255 * (scale - 0.2) * 5, 0, 255))
            elif scale <= (3/5):
                strip.set_pixel(i, (255, 0, 255 * (1 - (scale - 0.4) * 5)))
            elif scale <= (4/5):
                strip.set_pixel(i, (255, 255 * (scale - 0.6) * 5, 0))
            else:
                strip.set_pixel(i, (255 * (1 - (scale - 0.8) * 5), 255, 0))
            
            time.sleep(1/11)
            strip.show()
             
        if offset < 10:
            offset += 1
        else:
            offset = 0
        
        count += 1
        
try:
    connect('HoopCafeBMT2.4G', 'Glynster73')
except KeyboardInterrupt:
    sys.exit()

print('Connected')

# initialize data
latitude = 51.04
longitude = -114.07
lcd.clear()
lcd.move_to(0,0)
lcd.putstr(f'Recieving Data..')
url = 'https://api.open-meteo.com/v1/forecast?latitude=' + str(latitude) + '&longitude=' + str(longitude)+ '&hourly=temperature_2m,weather_code,wind_speed_10m,wind_direction_10m&timezone=auto'
print(url)
r = urequests.get(url)
data = r.json()
r.close()
print(data)

# f = open('data.json')
# data = json.load(f)

# custom characters
lcd.custom_char(0, bytearray([
0x02,
0x05,
0x02,
0x00,
0x00,
0x00,
0x00,
0x00
        ]))

def menu():
    num_options = 7
    cur_option = 0
    
    while True:
        time.sleep(0.1)
        option = round(adc.read_u16() / pot_max * (num_options - 1)) + 1
        
        options = ('Temperature', 'Wind Speed', 'Weather Code', 'Change Lat/Long','Brightness', 'Update', 'Power Off', '')
        
        if option != cur_option:
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr(f'>{options[option - 1]}')
            lcd.move_to(0,1)
            lcd.putstr(f'{options[option]}')
        
        if button.value() == 0:
            return option
        
        cur_option = option
        
def update_data():
    lcd.clear()
    lcd.move_to(0,0)
    lcd.putstr(f'Recieving Data..')
    
    url = 'https://api.open-meteo.com/v1/forecast?latitude=' + str(latitude) + '&longitude=' + str(longitude)+ '&hourly=temperature_2m,weather_code,wind_speed_10m,wind_direction_10m&timezone=auto'
    print(url)
    r = urequests.get(url)
    data = r.json()
    r.close()
    print(data)

    return data
    
def get_scale(parameter):
    max_value = data['hourly'][parameter][0]
    min_value = data['hourly'][parameter][0]
    for value in data['hourly'][parameter]:
        if value > max_value:
            max_value = value
            
        if value < min_value:
            min_value = value

    value_diff = max_value - min_value
    
    return (min_value, value_diff, max_value)

def weather(code):
    weather = ['Fair', 'Mainly Clear', 'Partly Cloudy', 'Overcast','', '', '', '', '', '',
               '', '', '', '', '', '', '', '', '', '',
               '', '', '', '', '', '', '', '', '', '',
               '', '', '', '', '', '', '', '', '', '',
               '', '', '', '', '', 'Fog', '', '', '', '',
               '', 'Light Drizzle', '', 'Moderate Drizzle', '', '', '', '', '', '',
               '', 'Slight Rain', '', 'Moderate Rain', '', '', '', '', '', '',
               '', 'Slight Snow', '', 'Moderate Snow', '', '', '', '', '', '',
               'Slight Showers', '', '', '', '', '', '', '', '', '',
               '', '', '', '', '', '', '', '', '', '',]
    
    return weather[code]

selection = menu()

def off():
    lcd.clear()
    strip.fill((0,0,0))
    strip.show()
    while True:
        if button.value() == 0:
            break

offset = 0
while True:
    time.sleep(0.5)
    if button.value() == 0:
        selection = menu()
    
    for i in list(range(numpix))[::-1]:
        
        if offset < (168 - i):
            j = i + offset
        else:
            j = i + offset - 168
        
        if i == 0:
            temp = data['hourly']['temperature_2m'][j]
            date = data['hourly']['time'][j][5:10]
            date_time = data['hourly']['time'][j][11:]
            weather_code = data['hourly']['weather_code'][j]
            wind_speed = data['hourly']['wind_speed_10m'][j]
            wind_direction = data['hourly']['wind_direction_10m'][j]
        
        if selection == 2:
            min_wind_speed = get_scale('wind_speed_10m')[0]
            wind_speed_diff = get_scale('wind_speed_10m')[1]
            scale = (data['hourly']['wind_speed_10m'][j] - min_wind_speed) / wind_speed_diff     
        elif selection == 3:
            min_weather_code = get_scale('weather_code')[0]
            weather_code_diff = get_scale('weather_code')[1]
            scale = (data['hourly']['weather_code'][j] - min_weather_code) / weather_code_diff
        else:
            min_temp = get_scale('temperature_2m')[0]
            temp_diff = get_scale('temperature_2m')[1]
            scale = (data['hourly']['temperature_2m'][j] - min_temp) / temp_diff
        
        if scale <= (1/5):
            strip.set_pixel(i, (0, 255 * (1 - scale * 5), 255))
        elif scale <= (2/5):
            strip.set_pixel(i, (255 * (scale - 0.2) * 5, 0, 255))
        elif scale <= (3/5):
            strip.set_pixel(i, (255, 0, 255 * (1 - (scale - 0.4) * 5)))
        elif scale <= (4/5):
            strip.set_pixel(i, (255, 255 * (scale - 0.6) * 5, 0))
        else:
            strip.set_pixel(i, (255 * (1 - (scale - 0.8) * 5), 255, 0))
        time.sleep(0.5/numpix)
        strip.show()
        
    if selection == 1:
        lcd.clear()
        lcd.move_to(0,0)
        lcd.putstr(f'Temp: {temp}')
        lcd.putchar(chr(0))
        lcd.putstr('C')
        lcd.move_to(0,1)
        lcd.putstr(f'{date} {date_time}')
        if button.value() == 0:
            selection = menu()
    elif selection == 2:
        lcd.clear()
        lcd.move_to(0,0)
        lcd.putstr(f'{wind_speed}km/h {wind_direction}')
        lcd.putchar(chr(0))
        lcd.move_to(0,1)
        lcd.putstr(f'{date} {date_time}')
        if button.value() == 0:
            selection = menu()
    elif selection == 3:
        lcd.clear()
        lcd.move_to(0,0)
        lcd.putstr(f'{weather(weather_code)}')
        lcd.move_to(0,1)
        lcd.putstr(f'{date} {date_time}')
        if button.value() == 0:
            selection == menu()
    elif selection == 4:
        while True:
            time.sleep(0.5)
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr(f'Lat: {latitude}')
            latitude = round(adc.read_u16() / pot_max * 180 - 90, 2)
            if button.value() == 0:
                break
        while True:
            time.sleep(0.5)
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr(f'Long: {longitude}')
            longitude = round(adc.read_u16() / pot_max * 360 - 180, 2)
            if button.value() == 0:
                break
        data = update_data()
        selection = menu()
    elif selection == 5:
        lcd.clear()
        lcd.move_to(0,0)
        lcd.putstr(f'Brightness:')
        lcd.move_to(0,1)
        lcd.putstr(f'{brightness}')
        brightness = round(adc.read_u16() / pot_max * 255, 0)
        strip.brightness(brightness)
        if button.value() == 0:
            selection == menu()
    elif selection == 6:
        data = update_data()
        selection = menu()
    elif selection == 7:
        off()
        selection = menu()
    
    # print(offset)
    if offset < 167:
        offset += 1
    else:
        offset = 0