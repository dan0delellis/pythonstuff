#!/usr/bin/env python3
import board, busio, adafruit_bme280, time, sched
from math import floor
import mysql.connector

#to do: make these arguments
database = "climate"
table = "readings"
location = "apartment"

s = sched.scheduler(time.time, time.sleep)
db = mysql.connector.connect(host="10.0.0.2", user="sensorsrecord", password="donkeyboner", database="climate")
mycursor = db.cursor()
i2c = busio.I2C(board.SCL, board.SDA)
#I may have fried my sensor by not paying attention to the 'Non-condensing' part of the humidity safety indication so now it reports on 0x76.
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c,address=0x76)

def getData():
    s.enter(3,1,getData)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    query = f"INSERT into {table} (timestamp, location, temp, humid, pressure ) VALUES ( %s, %s, %s, %s, %s)"
    val = (timestamp, location, bme280.temperature, bme280.humidity, bme280.pressure)
    mycursor.execute(query, val)
    db.commit()


s.enter(0,1,getData)
s.run()
