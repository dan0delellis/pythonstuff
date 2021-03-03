#!/usr/bin/python3
import datetime
import time
import sched
import requests
import json
import mysql.connector

s = sched.scheduler(time.time, time.sleep)

sqlURL = "10.2.0.2"
sqlUsr = "sensorsrecord"
sqlPw = "donkeyboner"
sqlDB = "climate"
sqlTable = "json"

def critFail(msg):
    print(f"{msg}")
    print("Exiting due to unrecoverable error.  Hopefully systemd won't retry.")
    exit(5)

def handleError(e):
    err = str(e)
    if "(HY000)" in err:
        print("Failed to connect to mysql at {sqlURL}: ({e})  Retrying in 300 seconds")
        sleep(300)
        exit(3)
    if "(28000)" in err:
        critFail(f"Authentication error connecting to {sqlURL}:{err}")
        critFail(err, meta)
    tooMany = "Not all parameters were used in the SQL statement"
    tooFew =  "Not enough parameters for the SQL statement"
    queryErrors = ["(21S01)", "(42000)", "(42S02)", tooMany, tooFew, "[Errno 2]"]
    for x in queryErrors:
        if (x in err):
            critFail(err)
    print(f"Unknown error: {err}")
    exit(7)

try:
    db = mysql.connector.connect(host=sqlURL, user=sqlUsr, password=sqlPw, database=sqlDB)
    mycursor = db.cursor()
    handleError(e)

    cityID = open("cityid", "r").read().strip()
    handleError(e)
    apiKey = open("apikey", "r").read().strip()
except Exception as e:
    handleError(e)

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
    try:
        mycursor.execute(query, val)
    except:
        handleError(e)

    temp = json["main"]["temp"] - 273.15
    humid = json["main"]["humidity"]
    pressure = json["main"]["pressure"]
    avgTS = json["dt"]
    location = json["name"]
    averagesQuery = "INSERT into averages (timestamp, location, temp, humid, pressure) VALUES (%s, %s, %s, %s, %s)"
    values = (avgTS, location, temp, humid, pressure)
    try:
        mycursor.execute(averagesQuery, values)
    except Exception as e:
        handleError(e)
    db.commit()

s.enter(1,0,getJson)
s.run()
