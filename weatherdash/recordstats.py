#!/usr/bin/env python3
import board
import busio
import adafruit_bme280
import redis
import time
import sched
from math import floor

s = sched.scheduler(time.time, time.sleep)

r = redis.Redis(host='10.0.0.2', port=6379, db=9)
expiry = 3600 * 24 * 7


i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

def getData():
    s.enter(3,1,getData)
    epoc = floor(time.time())
    r.set(f"{epoc}-temperature", bme280.temperature, ex=expiry)
    r.set(f"{epoc}-humidity", bme280.humidity, ex=expiry)
    r.set(f"{epoc}-pressure", bme280.pressure, ex=expiry)

s.enter(0,1,getData)
s.run()
