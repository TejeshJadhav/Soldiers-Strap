import subprocess
import time

import requests
import serial
import serial.tools.list_ports as Port

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont

connected = [port.device for port in Port.comports()]
arduino = serial.Serial(connected[0], 9600, timeout=.1)
# arduino.open()
RST = None    
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0
disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
disp.begin()
disp.clear()
disp.display()
width = disp.width
height = disp.height
image = Image.new('1', (width, height))
draw = ImageDraw.Draw(image)
draw.rectangle((0,0,width,height), outline=0, fill=0)
padding = -2
top = padding
bottom = height-padding
x = 0
font = ImageFont.load_default()

_id = 1
pulse = 123
lat=18.990201
lng=73.1254814
send_timeline_status = False
sos_status = False

def show_sos_msg():
    disp.clear()
    disp.display()

    # Load image based on OLED display height.  Note that image is converted to 1 bit color.
    if disp.height == 64:
        image = Image.open('sos.png').convert('1')
    else:
        image = Image.open('sos.png').convert('1')

    # Alternatively load a different format image, resize it, and convert to 1 bit color.
    #image = Image.open('happycat.png').resize((disp.width, disp.height), Image.ANTIALIAS).convert('1')

    # Display image.
    disp.image(image)
    disp.display() 
    time.sleep(10.50)

def show_data(pulse=321,_id=1,lat=12.3123512,lng=73.1254814):
    # Draw a black filled box to clear the image.
    disp.clear()
    disp.display()
    
    draw.rectangle((0,0,width,height), outline=0, fill=0)
    # Write two lines of text.

    draw.text((x, top),       "Soldier ID: " + str(_id), font=font, fill=255)
    draw.text((x, top+8),     "Heart Beat: " + str(pulse),  font=font, fill=255)
    draw.text((x, top+16),    "lat: " + str(lat),  font=font, fill=255)
    draw.text((x, top+25),    "lng: " + str(lng),  font=font, fill=255)
    # Display image.
    disp.image(image)
    disp.display()
    time.sleep(.1)


def send_location(pulse=123,temperature=85,sos=0,lat=18.990201,lng=73.1254814):
    # url = 'http://b03af618.ngrok.io/maps/soldier_post?sos={}&lat={t:2.7f}&lng={n:2.7f}'.format(sos,t=lat,n=lng)
    url = 'http://192.168.43.68/maps/soldier_post?temperature={}&pulse={}&sos={}&lat={t:2.7f}&lng={n:2.7f}'.format(temperature,pulse,sos,t=lat,n=lng)
    x = requests.get(url)
    # print(url)
    # if sos == '1':
        # print(x.text)

def send_timeline():
    for i in range(1,15,2):
        # print('%2.7f' % (18.990201 + i/1000))
        data = []
        if arduino.write('d'.encode()):
            x = arduino.readlines()
            for y in x:
                # print(y.decode().split(":")[1].split("\r\n")[0])
                data.append(y.decode().split(":")[1].split("\r\n")[0])
            if len(data) == 4:
                p = data[0]
                t = data[1]
                sos = data[2]
                demo = data[3] 
        send_location(pulse=p,lat = 18.990201 + i/100000, lng = 73.1254814 + i/100000)
        show_data(pulse=p,lat='{t:2.7f}'.format(t=18.990201 + i/100000), lng='{n:2.7f}'.format(n=73.1254814 + i/100000))

# send_timeline()
# show_sos_msg()
# while True:
show_data()
while True:
    data = []
    if arduino.write('d'.encode()):
        data_incomming = arduino.readlines()
        # print(x)
        for y in data_incomming:
            # print(y.decode().split(":")[1].split("\r\n")[0])
            data.append(y.decode().split(":")[1].split("\r\n")[0])
    time.sleep(2)

    if len(data) == 4:
        p = data[0]
        t = data[1]
        sos = data[2]
        demo = data[3] 
           # print(type(data[0]))
        # print(type(sos), sos)
        if sos == '1':
            show_sos_msg()
            send_location(temperature=t,pulse=p,sos=sos)
        elif demo == '1':
            send_timeline()
        else:
            send_location(temperature=t,pulse=p,sos=sos)
            show_data(pulse=p) 
