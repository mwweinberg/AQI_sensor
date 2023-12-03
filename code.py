import time
import board
import busio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.i2c import PM25_I2C
from adafruit_funhouse import FunHouse

#for the external API
import adafruit_requests as requests
import keys
import socketpool
import ssl
import wifi

#for the light sensor mapping
from adafruit_simplemath import map_range


reset_pin = None

funhouse = FunHouse(default_bg=None)

# Create library object, use 'slow' 100KHz frequency!
i2c = board.I2C()
# Connect to a PM2.5 sensor over I2C
pm25 = PM25_I2C(i2c, reset_pin)

print("Found PM2.5 sensor, reading data...")

# Turn on WiFi
funhouse.network.enabled = True
print("wifi on")
# Connect to WiFi
funhouse.network.connect()
print("wifi connected")

#these variables sets up the requests
pool = socketpool.SocketPool(wifi.radio)
#requests = requests.Session(pool, ssl.create_default_context())
requests = funhouse.network._wifi.requests


#IO Stuff
FEED_2_5 = "2pointfive"
TEMP_FEED = "temp"
HUM_FEED = "humidity"
TEMPERATURE_OFFSET = (
    8  # Degrees C to adjust the temperature to compensate for board produced heat
)

#Colors
BLACK = (0,0,0)
GREEN = (0,228,0)
YELLOW = (255, 255, 0)
ORANGE = (255,40,0)
RED = (255,0,0)
PURPLE = (143,63,151)
MAROON = (126,0,35)

#text
funhouse.display.show(None)
pm_label = funhouse.add_text(
    text_scale = 2, text_position = (10,10), text_color = 0x606060
)
pm_value = funhouse.add_text(
    text_scale = 12, text_position = (90,60), text_color = 0x606060
)
aqi_label = funhouse.add_text(
    text_scale = 2, text_position = (10,110), text_color = 0x606060
)
aqi_value = funhouse.add_text(
    text_scale = 12, text_position = (60,180), text_color = 0x606060
)
funhouse.display.show(funhouse.splash)

counter = 0

while True:
    try:
        aqdata = pm25.read()
        # print(aqdata)
    except RuntimeError:
        print("Unable to read from sensor, retrying...")
        continue

    #IO Stuff
     
    # Push to IO using REST
    try:
        funhouse.push_to_io(FEED_2_5, aqdata["pm25 env"])
        #does the temp offset and converts C to F
        funhouse.push_to_io(TEMP_FEED, ((funhouse.peripherals.temperature - TEMPERATURE_OFFSET)*9 / 5 + 32))
        funhouse.push_to_io(HUM_FEED, funhouse.peripherals.relative_humidity)
        print("data pushed")
    except:
        print("error uploading data, moving on")
    

    
    # get remote AQI data
    # #https://learn.adafruit.com/adafruit-funhouse/getting-the-date-time   
    target_URL = keys.AQI_URL
    
    if counter == 0:
        try:
            response = requests.get(target_URL, timeout = 10)
            #print(response)
            jsonResponse = response.json()
            print(jsonResponse[0]["AQI"])
            currentAQI = jsonResponse[0]["AQI"]
            counter += 1
        except:
            currentAQI = 0
            print('request failed')
    if 0 < counter < 8:
        counter += 1
        print("counting up, now at " + str(counter))
    if counter > 7:
        counter = 0
        print("reset counter")
    

    #text stuff
    #set the label
    funhouse.set_text("PM 2.5", pm_label)
    #set the color for the pm2.5 reading
    if aqdata["pm25 env"] <= 12.0:
        funhouse.set_text_color(GREEN, pm_value)
    elif 12.0 < aqdata["pm25 env"] <= 35.4:
        funhouse.set_text_color(YELLOW, pm_value)
    elif 35.4 < aqdata["pm25 env"] <= 55.4:
        funhouse.set_text_color(ORANGE, pm_value)   
    elif 55.4 < aqdata["pm25 env"] <= 150.4:
        funhouse.set_text_color(RED, pm_value)
    elif 15.4 < aqdata["pm25 env"] <= 250.4:
        funhouse.set_text_color(PURPLE, pm_value)
    elif 25.4 < aqdata["pm25 env"] <= 500.4:
        funhouse.set_text_color(MAROON, pm_value)
    #set the reading
    funhouse.set_text(aqdata["pm25 env"], pm_value)
    #set the aqi label
    funhouse.set_text("AQI", aqi_label)
    #set the aqi color
    if currentAQI <= 50.0:
        funhouse.set_text_color(GREEN, aqi_value)
    elif 50.0 < currentAQI <= 100:
        funhouse.set_text_color(YELLOW, aqi_value)
    elif 100 < currentAQI <= 150:
        funhouse.set_text_color(ORANGE, aqi_value)   
    elif 150 < currentAQI <= 200:
        funhouse.set_text_color(RED, aqi_value)
    elif 200 < currentAQI <= 300:
        funhouse.set_text_color(PURPLE, aqi_value)
    elif 300 < currentAQI <= 500:
        funhouse.set_text_color(MAROON, aqi_value)
    funhouse.set_text(currentAQI, aqi_value)


    #LED Stuff
    #https://www.airnow.gov/sites/default/files/2020-05/aqi-technical-assistance-document-sept2018.pdf
    #set all of the LEDs to black by default
    led_0 = BLACK
    led_1 = BLACK
    led_2 = BLACK
    led_3 = BLACK
    led_4 = BLACK
    print ("2.5 = " + str(aqdata["pm25 env"]))

    #update first two leds depending on the 2.5 reading
    if aqdata["pm25 env"] <= 12.0:
        led_0 = GREEN
        led_1 = GREEN
    elif 12.0 < aqdata["pm25 env"] <= 35.4:
        led_0 = YELLOW
        led_1 = YELLOW
    elif 35.4 < aqdata["pm25 env"] <= 55.4:
        led_0 = ORANGE
        led_1 = ORANGE   
    elif 55.4 < aqdata["pm25 env"] <= 150.4:
        led_0 = RED
        led_1 = RED 
    elif 15.4 < aqdata["pm25 env"] <= 250.4:
        led_0 = PURPLE
        led_1 = PURPLE 
    elif 25.4 < aqdata["pm25 env"] <= 500.4:
        led_0 = MAROON
        led_1 = MAROON

    #update the last two LEDs based on AQI
    if currentAQI <= 50.0:
        led_3 = GREEN
        led_4 = GREEN
    elif 50.0 < currentAQI <= 100:
        led_3 = YELLOW
        led_4 = YELLOW
    elif 100 < currentAQI <= 150:
        led_3 = ORANGE
        led_4 = ORANGE   
    elif 150 < currentAQI <= 200:
        led_3 = RED
        led_4 = RED
    elif 200 < currentAQI <= 300:
        led_3 = PURPLE
        led_4 = PURPLE
    elif 300 < currentAQI <= 500:
        led_3 = MAROON
        led_4 = MAROON


    #update the LEDs
    funhouse.peripherals.set_dotstars(led_0, led_1, led_2, led_3, led_4)

    #set LED brightness so they aren't super bright at night
    #map_range works (inputnumber, orig min, orig max, new min, new max)
    #right reading bounds appear to be ~1800-54000, real world is closer to 1800-5000)
    #goal here is to make the lights bright when it is bright and dim when it is dark
    brightness = map_range(funhouse.peripherals.light, 1000, 8000, 0, 1)
    print(brightness)
    funhouse.peripherals.dotstars.brightness = brightness

    time.sleep(120)
