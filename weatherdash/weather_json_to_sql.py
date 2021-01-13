#!/usr/bin/python3
import datetime
import time
import sched
import requests
import json
import mysql.connector

s = sched.scheduler(time.time, time.sleep)

sqlURL = "10.0.0.2"
sqlUsr = "sensorsrecord"
sqlPw = "donkeyboner"
sqlDB = "climate"
sqlTable = "json"

db = mysql.connector.connect(host=sqlURL, user=sqlUsr, password=sqlPw, database=sqlDB)
mycursor = db.cursor()

cityID = open("cityid", "r").read().strip()
apiKey = open("apikey", "r").read().strip()

url = f"https://api.openweathermap.org/data/2.5/weather?id={cityID}&appid={apiKey}&units=standard"

def getJson():
    s.enter(600, 0, getJson)
    curl_response = requests.get(url)
    curl_response.encoding = 'utf-8'
    data = curl_response.text
    json = curl_response.json()

#note to self: next time you start a project, decide on either UTC datetime OR unix epoc. don't mix them.
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    query = f"INSERT into {sqlTable} (timestamp, location_code, report_json ) VALUES ( %s, %s, %s)"
    val = (timestamp, cityID, data)
    mycursor.execute(query, val)

    temp = json["main"]["temp"] - 273.15
    humid = json["main"]["humidity"]
    pressure = json["main"]["pressure"]
    avgTS = json["dt"]
    location = json["name"]
    averagesQuery = "INSERT into averages (timestamp, location, temp, humid, pressure) VALUES (%s, %s, %s, %s, %s)"
    values = (avgTS, location, temp, humid, pressure)
    mycursor.execute(averagesQuery, values)
    db.commit()

s.enter(1,0,getJson)
s.run()
