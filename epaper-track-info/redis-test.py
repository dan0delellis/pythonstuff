#!/usr/bin/env python3

import requests
import json
import redis
import pickle
import emoji
from requests.auth import HTTPBasicAuth

r = redis.Redis(host='10.0.0.2', port=6379, db=10)

source = {
        "url":"http://localhost:8080/requests/status.json",   
        "user":"",
        "password":"herpderp"
        }

curl_response = requests.get(source["url"], auth=HTTPBasicAuth(source["user"],source["password"]))
curl_response.encoding = 'utf-8'

data = curl_response.json()
print(emoji.emojize("Hello 🌎", use_aliases=True))

#Initialize the dict
info = {}

meta_fields = ['artist', 'title', 'album']
root_fields = ['length', 'time', 'position']

#Make sure the fields are actually set to something before trying to assign them in a dict.
#It also ensures that each value will get updated when the track changes
for i in meta_fields:
    if i in data['information']['category']['meta'].keys():
        info[i] = data['information']['category']['meta'][i]
    else:
        info[i] = '[unknown {}]'.format(i)

for j in root_fields:
    if j in data.keys():
        info[j] = data[j]
    else:
        info[j] = -1

info_pickled = pickle.dumps(info)
r.set("track_info", info_pickled)

#Test the output
get_data = r.get("track_info")
get_data_unpickled = pickle.loads(get_data)


for i in get_data_unpickled.keys():
    print('{}: {}'.format(i, get_data_unpickled[i]))
