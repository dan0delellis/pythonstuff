#!/usr/bin/env python3

import requests
import json
import redis
import pickle
import time
import sched
from requests.auth import HTTPBasicAuth

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

def getInfo():
    printState("starting ")
    info = initDict()
#    printState("Dict Init")
    curl_response = requests.get(source["url"], auth=HTTPBasicAuth(source["user"],source["password"]))
    curl_response.encoding = 'utf-8'
#    printState("data curl")
    data = curl_response.json()

    for i in meta_fields:
        if i in data['information']['category']['meta'].keys():
            info[i] = data['information']['category']['meta'][i]

    for j in root_fields:
        if j in data.keys():
            info[j] = data[j]
#    printState("parsedd  ")

    info_pickled = pickle.dumps(info,protocol=0)
    r.set("track_info", info_pickled)
    printState("data set ")

getInfo()
#Test the output
get_data = r.get("track_info")
get_data_unpickled = pickle.loads(get_data)


for i in get_data_unpickled.keys():
    print('{}: {}'.format(i, get_data_unpickled[i]))
