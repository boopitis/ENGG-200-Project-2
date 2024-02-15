from machine import Pin, I2C, ADC
from neopixel import Neopixel
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
import neopixel
import urequests
import time
import network
import json

def connect(ssid, wait, password=0):
    # Connect to WLAN
    # Connect function from https://projects.raspberrypi.org/en/projects/get-started-pico-w/2
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if password == 0:
        wlan.connect(ssid)
    else:
        wlan.connect(ssid, password) # Remove password if using airuc-guest
    
    count = 0
    while wlan.isconnected() == False and count < wait:
        print(f'Waiting for connection to {ssid}')
        count += 1
        time.sleep(1)
        
    if wlan.isconnected() == False:
        exit()
    else:
        print('Connected.')

# initialize LCD
I2C_ADDR     = 63
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

i2c = I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

# initialize LED strip
numpix = 30
strip = Neopixel(numpix, 0 , 4, "RGB")
strip.brightness(10)

# initialize small LEDs
red_led = Pin(13, Pin.OUT)
yel_led = Pin(12, Pin.OUT)
blu_led = Pin(16, Pin.OUT)
gre_led = Pin(17, Pin.OUT)

# initialize potentiometer
adc = ADC(Pin(26))
pot_max = 65535

# initialize button
button = Pin(5, Pin.IN, Pin.PULL_DOWN)

latitude = 51.04
longitude = -114.07

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

# try:
#     connect('HoopCafeMain', 25, 'Glynster73')
# except KeyboardInterrupt:
#     machine.reset()
#     
# # initialize data
# url = 'https://api.open-meteo.com/v1/forecast?latitude=' + str(latitude) + '&longitude=' + str(longitude) + '&hourly=temperature_2m,weather_code&timezone=auto'
# print(url)
# r = urequests.get(url)
# data = r.json()
# r.close()

f = open('data.json')
data = json.load(f)

cur_option = 0
def menu():
    num_options = 4
    
    while True:
        option = round(adc.read_u16() / pot_max * (num_options - 1)) + 1
        
        options = ('Temp/Date', 'Change Lat/Long', 'Weather Code', 'Exit', '')
        
        if option != cur_option:
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr(f'>{options[option - 1]}')
            lcd.move_to(0,1)
            lcd.putstr(f'{options[option]}')
        
        if button.value():
            return option
        
        cur_option = option
        time.sleep(0.25)

def show_small_leds(weather_code):
    if weather_code in (0, 1):
        red_led.on()
    else:
        red_led.off()
        
    if weather_code in (2, 3) or 40 <= weather_code < 50:
        yel_led.on()
    else:
        yel_led.off()
        
    if 50 <= weather_code < 70 or weather_code in (80, 81, 82, 87, 88, 89, 90, 91, 92, 95, 96, 97, 98):
        blu_led.on()
    else:
        blu_led.off()
        
    if 70 <= weather_code < 80 or weather_code in (83, 84, 85, 86, 87, 88, 89, 90, 93, 94, 97, 99):
        gre_led.on()
    else:
        gre_led.off()
        
def update_data():
    url = 'https://api.open-meteo.com/v1/forecast?latitude=' + str(latitude) + '&longitude=' + str(longitude) + '&hourly=temperature_2m,weather_code&timezone=auto'
    r = urequests.get(url)
    data = r.json()
    r.close()
    
def get_scale(parameter):
    max_value = data['hourly'][parameter][0]
    min_value = data['hourly'][parameter][0]
    for value in data['hourly'][parameter]:
        if value > max_value:
            max_value = value
            
        if value < min_value:
            min_value = value

    value_diff = max_value - min_value
    
    return (min_value, value_diff)

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

min_temp = get_scale('temperature_2m')[0]
temp_diff = get_scale('temperature_2m')[1]

offset = 0
selection = 1
while True:
    
    if button.value():
        selection = menu()
    
    for i in range(30):
        if offset < (168 - i):
            j = i + offset
        else:
            j = i + offset - 168
            
        if i == 0:
            temp = data['hourly']['temperature_2m'][j]
            date = data['hourly']['time'][j][5:10]
            date_time = data['hourly']['time'][j][11:]
            weather_code = data['hourly']['weather_code'][j]
            
        scale = (data['hourly']['temperature_2m'][j] - min_temp) / temp_diff
        
        if scale <= (1/5):
            strip.set_pixel(i, (0, 255 * (1 - scale * 5), 255))
        elif scale <= (2/5):
            strip.set_pixel(i, (255 * scale * 5/2, 0, 255))
        elif scale <= (3/5):
            strip.set_pixel(i, (255, 0, 255 * (1 - scale * 5/3)))
        elif scale <= (4/5):
            strip.set_pixel(i, (255, 255 * scale * 5/4, 0))
        else:
            strip.set_pixel(i, (255 * (1 - scale), 255, 0))
    strip.show()
    
    show_small_leds(weather_code)
    
    if selection == 1:
        lcd.clear()
        lcd.move_to(0,0)
        lcd.putstr(f'Temp: {temp}')
        lcd.putchar(chr(0))
        lcd.putstr('C')
        lcd.move_to(0,1)
        lcd.putstr(f'{date} {date_time}')
    elif selection == 2:
        while True:
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr(f'Lat: {latitude}')
            lcd.move_to(0,1)
            lcd.putstr(f'Long: {longitude}')
            latitude = round(adc.read_u16() / pot_max * 360 - 180, 2)
            if button.value():
                break
        while True:
            lcd.clear()
            lcd.move_to(0,0)
            lcd.putstr(f'Lat: {latitude}')
            lcd.move_to(0,1)
            lcd.putstr(f'Long: {longitude}')
            longitude = round(adc.read_u16() / pot_max * 360 - 180, 2)
            if button.value():
                break
        update_data()
    elif selection == 3:
        lcd.clear()
        lcd.move_to(0,0)
        lcd.putstr(f'{weather(weather_code)}')
        lcd.move_to(0,1)
        lcd.putstr(f'{date} {date_time}')
    elif selection == 4:
        lcd.clear()
        strip.fill((0,0,0))
        break
        
    # print(offset)
    if offset < 167:
        offset += 1
    else:
        offset = 0
        
    time.sleep(0.5)