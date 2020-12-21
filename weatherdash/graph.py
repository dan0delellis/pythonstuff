#!/usr/bin/env python3

import redis
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from matplotlib import cbook as cbook
import mysql.connector as sql
from datetime import timedelta, datetime

datetimeString = "%Y-%m-%d %H:%M:%S"
db = sql.connect(host="10.0.0.2", user="sensorsrecord", password="donkeyboner", database="climate")

endTimeStamp = datetime.now()
lookbackRange = 24 * timedelta(hours=1)
startTimeStamp = endTimeStamp - lookbackRange


matplotlib.use('TkAgg')

cursor = db.cursor()

sql = "Select timestamp, temp from readings where timestamp <= %s and timestamp >= %s"
var = (endTimeStamp.strftime(datetimeString), startTimeStamp.strftime(datetimeString))

cursor.execute(sql,var)
result = cursor.fetchall()
x = []
y = []
for i in result:
    y.append(i[1])
    x.append(i[0])

print(datetime.now())
plt.plot(x, y, label="temp")
print(datetime.now())
plt.show()
print(datetime.now())


