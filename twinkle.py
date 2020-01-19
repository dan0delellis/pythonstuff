#!/usr/bin/env python
# Simple demo of of the WS2801/SPI-like addressable RGB LED lights.
import time
import random
import RPi.GPIO as GPIO

# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI


# Configure the count of pixels:
PIXEL_COUNT = 300

# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
SPI_PORT   = 0
SPI_DEVICE = 0
pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)


# Define the wheel function to interpolate between different hues.
class LED:
  def __init__(self, st, color, num):
    self.num = num
    self.status = st
    self.on_duration = get_duration()
    self.off_duration = get_duration()
    self.color_static = color_map[color]
    self.color = self.color_static
    self.duration = self.on_duration
    self.cycles = get_cycle_count(self.on_duration, self.off_duration, 8, 10, 25)

colors = ["red", "ylw", "grn", "tel", "blu", "prp", "wht"]
brightness = 1
lum = int(brightness*255)

color_map = {
    "off": [0,0,0],
    "red": [lum, 0, 0],
    "prp": [lum,0,lum],
    "grn": [0, lum, 0 ],
    "ylw": [lum, lum, 0],
    "blu": [0, 0, lum],
    "tel": [0,lum,lum],
    "wht": [lum,lum,lum]

}

def get_cycle_count(on, off, hours, fade_minutes, tick_ms):
    total_duration = float((on + off) * float(tick_ms)/1000)
    min_cycles = float((hours*3600)/total_duration)
    extra_cycles = float(fade_minutes * 60)/total_duration * random.random()
    return int(min_cycles + extra_cycles)


def get_duration():
    base = random.randint(50,100)
    extra = int(random.gauss(200,50))
    extra = max(150,extra)
    extra = min(250,extra)
    return base+extra

def process_led(led):
    led.duration -= 1
    if (led.cycles > 0):
        if (led.duration == 0 ):
            led.status = (led.status + 1) % 2
            if (led.status == 0):
                led.cycles -= 1
                led.duration = led.off_duration
                led.color = color_map["off"]
            else:
                led.duration = led.on_duration
                led.color = led.color_static
    else:
        led.status == 0




if __name__ == "__main__":
    leds = [0] * pixels.count()

    for i in range(pixels.count()):
        leds[i]=LED(0, colors[i % len(colors)], i)

    # Clear all the pixels to turn them off.
    pixels.clear()
    pixels.show()  # Make sure to call show() after changing any pixels!
    print pixels.count()
    remainingCycles = 1
    start = int(round(time.time() * 1000))
    while remainingCycles > 0:
        remainingCycles = 0
        for i in range(pixels.count()):
            remainingCycles = remainingCycles + leds[i].cycles
            process_led(leds[i])
            pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( leds[i].color[0], leds[i].color[1], leds[i].color[2]))
        pixels.show()
    duration = int(round(time.time() * 1000)) - start
