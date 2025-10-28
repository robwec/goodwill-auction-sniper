import requests
import os
import re
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from dateutil import parser, tz
import pytz

userpass = json.load(open('nobackup/userpass.json', 'r'))
sess = requests.Session()
resp = sess.get('https://shopgoodwill.com/signin')

headers = {
    'authority': 'buyerapi.shopgoodwill.com',
    'accept': 'application/json',
    'accept-language': 'en-US,en;q=0.8',
    'access-control-allow-credentials': 'true',
    'access-control-allow-origin': '*',
    'content-type': 'application/json',
    'origin': 'https://shopgoodwill.com',
    'sec-ch-ua': '"Brave";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
}

json_data = {
    'userName': '[][][]', #obtained from monitoring backend request while logging in
    'password': '[][][]', #obtained from monitoring backend request while logging in
    'remember': False,
    'appVersion': 'c24fcf04d1d782f2',
    'browser': 'chrome',
}

resp = sess.post('https://buyerapi.shopgoodwill.com/api/SignIn/Login', headers=headers, json=json_data)
print(resp)
newbearer = resp.json()['accessToken']
json.dump(newbearer, open('nobackup/bearer.json', 'w'))
print("obtained new bearer:\n", newbearer)
