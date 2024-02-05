from machine import Pin, ADC
import time

button = Pin(14, Pin.IN, Pin.PULL_UP)

# initialize potentiometer
adc = ADC(Pin(26))
pot_max = 65535

current_option = 0
def menu():
    global current_option
    num_options = 4
    
    while True:
        time.sleep(0.1)
        option = round(adc.read_u16() / pot_max * (num_options - 1)) + 1
        print(option)
        options = ('Temp/Date', 'Change Lat/Long', 'Weather Code', 'Exit', '')
        
        if option != current_option:
            print(options[option])
        
        if button.value() == 0:
            return option
        
        current_option = option

selection = 0
latitude = 0
longitude = 0
while True:
    time.sleep(0.1)
    if button.value() == 0:
        print('button pressed')
        selection = menu()
    
    if selection == 1:
        print('selection 1 :3')
    elif selection == 2:
        while True:
            latitude += 1
            print(f'latitude: {latitude}')
            time.sleep(0.1)
            if button.value() == 0:
                break
        while True:
            longitude += 1
            print(f'longitude: {longitude}')
            time.sleep(0.1)
            if button.value() == 0:
                break
    elif selection == 3:
        print('weather uwu')
    elif selection == 4:
        print('goodbye world')
        break
