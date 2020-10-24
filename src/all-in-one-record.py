#!/usr/bin/env python3


from datetime import datetime
import csv
import numpy as np
import time
import colorsys
import sys
import ST7735
try:
    # Transitional fix for breaking change in LTR559
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

from bme280 import BME280
from pms5003 import PMS5003, ReadTimeoutError as pmsReadTimeoutError
from enviroplus import gas
from subprocess import PIPE, Popen
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from fonts.ttf import RobotoMedium as UserFont
import logging

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

logging.info("""all-in-one.py - Displays readings from all of Enviro plus' sensors

Press Ctrl+C to exit!

""")

# BME280 temperature/pressure/humidity sensor
bme280 = BME280()

# PMS5003 particulate sensor
pms5003 = PMS5003()

# Create ST7735 LCD display class
st7735 = ST7735.ST7735(
    port=0,
    cs=1,
    dc=9,
    backlight=12,
    rotation=270,
    spi_speed_hz=10000000
)

# Initialize display
st7735.begin()

RECORD_SECONDS_INTERVAL = 60
CSV_LOG_FILE = '../data/reading_data_{}.csv'.format(datetime.now().strftime("%Y%m%d_%H%M%S"))
WIDTH = st7735.width
HEIGHT = st7735.height

# Set up canvas and font
img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)
font_size = 20
font = ImageFont.truetype(UserFont, font_size)

message = ""

# The position of the top bar
top_pos = 25


# Displays data and text on the 0.96" LCD
def display_text(variable, data, unit):
    # Maintain length of list
    values[variable] = values[variable][1:] + [data]
    # Scale the values for the variable between 0 and 1
    vmin = min(values[variable])
    vmax = max(values[variable])
    colours = [(v - vmin + 1) / (vmax - vmin + 1) for v in values[variable]]
    # Format the variable name and value
    message = "{}: {:.1f} {}".format(variable[:4], data, unit)
    logging.info(message)
    draw.rectangle((0, 0, WIDTH, HEIGHT), (255, 255, 255))
    for i in range(len(colours)):
        # Convert the values to colours from red to blue
        colour = (1.0 - colours[i]) * 0.6
        r, g, b = [int(x * 255.0) for x in colorsys.hsv_to_rgb(colour, 1.0, 1.0)]
        # Draw a 1-pixel wide rectangle of colour
        draw.rectangle((i, top_pos, i + 1, HEIGHT), (r, g, b))
        # Draw a line graph in black
        line_y = HEIGHT - (top_pos + (colours[i] * (HEIGHT - top_pos))) + top_pos
        draw.rectangle((i, line_y, i + 1, line_y + 1), (0, 0, 0))
    # Write the text at the top in black
    draw.text((0, 0), message, font=font, fill=(0, 0, 0))
    st7735.display(img)


# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE, universal_newlines=True)
    output, _error = process.communicate()
    return float(output[output.index('=') + 1:output.rindex("'")])


# Tuning factor for compensation. Decrease this number to adjust the
# temperature down, and increase to adjust up
factor = 2.25

cpu_temps = [get_cpu_temperature()] * 5

delay = 0.5  # Debounce the proximity tap
mode = 0     # The starting mode
last_page = 0
light = 1

# Create a values dict to store the data
variables = ["timestamp",
             "temperature",
             "pressure",
             "humidity",
             "light",
             "oxidised",
             "reduced",
             "nh3",
             "pm1",
             "pm25",
             "pm10"]

values = {}

reading = {k: [] for k in variables}
last_record_time = int(time.time())

for v in variables:
    values[v] = [1] * WIDTH

# Create header of new CSV file
csv_header = variables
with open(CSV_LOG_FILE, 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = csv_header) 
    writer.writeheader()

# The main loop
try:
    while True:

        proximity = ltr559.get_proximity()

        # If the proximity crosses the threshold, toggle the mode
        if proximity > 1500 and time.time() - last_page > delay:
            mode += 1
            mode %= len(variables)
            last_page = time.time()
        
        if True:
            variable = "timestamp"
            data = time.time()
            reading[variable].append(data)
        # One mode for each variable
        if True:
            variable = "temperature"
            unit = "C"
            cpu_temp = get_cpu_temperature()
            # Smooth out with some averaging to decrease jitter
            cpu_temps = cpu_temps[1:] + [cpu_temp]
            avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
            raw_temp = bme280.get_temperature()
            data = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
            reading[variable].append(data)
        if mode == 0:
            display_text(variables[mode], data, unit)

        if True:
            variable = "pressure"
            unit = "hPa"
            data = bme280.get_pressure()
            reading[variable].append(data)
        if mode == 1:
            display_text(variables[mode], data, unit)

        if True:
            variable = "humidity"
            unit = "%"
            data = bme280.get_humidity()
            reading[variable].append(data)
        if mode == 2:
            display_text(variables[mode], data, unit)

        if True:
            variable = "light"
            unit = "Lux"
            if proximity < 10:
                data = ltr559.get_lux()
            else:
                data = 1
            reading[variable].append(data)
        if mode == 3:
            display_text(variables[mode], data, unit)

        if True:
            variable = "oxidised"
            unit = "kO"
            data = gas.read_all()
            data = data.oxidising / 1000
            reading[variable].append(data)
        if mode == 4:
            display_text(variables[mode], data, unit)

        if True:
            variable = "reduced"
            unit = "kO"
            data = gas.read_all()
            data = data.reducing / 1000
            reading[variable].append(data)
        if mode == 5:
            display_text(variables[mode], data, unit)

        if True:
            variable = "nh3"
            unit = "kO"
            data = gas.read_all()
            data = data.nh3 / 1000
            reading[variable].append(data)
        if mode == 6:
            display_text(variables[mode], data, unit)

        if True:
            variable = "pm1"
            unit = "ug/m3"
            try:
                data = pms5003.read()
            except pmsReadTimeoutError:
                logging.warning("Failed to read PMS5003")
            else:
                data = float(data.pm_ug_per_m3(1.0))
                reading[variable].append(data)
                if mode == 7:
                    display_text(variables[mode], data, unit)

        if True:
            variable = "pm25"
            unit = "ug/m3"
            try:
                data = pms5003.read()
            except pmsReadTimeoutError:
                logging.warning("Failed to read PMS5003")
            else:
                data = float(data.pm_ug_per_m3(2.5))
                reading[variable].append(data)
                if mode == 8:
                    display_text(variables[mode], data, unit)

        if True:
            variable = "pm10"
            unit = "ug/m3"
            try:
                data = pms5003.read()
            except pmsReadTimeoutError:
                logging.warning("Failed to read PMS5003")
            else:
                data = float(data.pm_ug_per_m3(10))
                reading[variable].append(data)
                if mode == 9:
                    display_text(variables[mode], data, unit)

        if int(time.time()) > (last_record_time+RECORD_SECONDS_INTERVAL):
            reading_avg = {k: np.mean(reading[k]) for k in reading.keys()}
            reading_avg['timestamp'] = int(time.time())
            with open(CSV_LOG_FILE, 'a') as csvfile: 
                writer = csv.DictWriter(csvfile, fieldnames = csv_header) 
                # writer.writeheader()
                writer.writerow(reading_avg) 
            reading = {k: [] for k in variables}
            last_record_time = time.time()

# Exit cleanly
except KeyboardInterrupt:
    sys.exit(0)
