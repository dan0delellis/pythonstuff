#!/usr/bin/env python3

import requests
import json
import redis
import pickle
import time
import sched
from requests.auth import HTTPBasicAuth
scheduler = sched.scheduler(time.time, time.sleep)

r = redis.Redis(host='10.0.0.2', port=6379, db=10)

source = {
        "url":"http://localhost:8080/requests/status.json",
        "user":"",
        "password":"herpderp"
        }

meta_fields = ['artist', 'title', 'album']
root_fields = ['length', 'time', 'position']

def initDict():
    info = {}
    for i in meta_fields:
        info[i] = '[unknown {}]'.format(i)
    for j in root_fields:
        info[j] = -1
    return info

def printState(state):
    print('{}: {}'.format(state, time.time()))

def readInfo():
    get_data = r.get("track_info")
    get_data_unpickled = pickle.loads(get_data)


    for i in get_data_unpickled.keys():
        print('{}: {}'.format(i, get_data_unpickled[i]))

def getInfo():
    scheduler.enter(0.25,1,getInfo)
    printState("starting ")
    info = initDict()
    curl_response = requests.get(source["url"], auth=HTTPBasicAuth(source["user"],source["password"]))
    curl_response.encoding = 'utf-8'
    data = curl_response.json()

    for i in meta_fields:
        if i in data['information']['category']['meta'].keys():
            info[i] = data['information']['category']['meta'][i]

    for j in root_fields:
        if j in data.keys():
            info[j] = data[j]

    info_pickled = pickle.dumps(info,protocol=0)
    r.set("track_info", info_pickled)
    printState("data set ")
    readInfo()
    printState("data read")


scheduler.enter(0,1,getInfo)
scheduler.run()
#Test the output
