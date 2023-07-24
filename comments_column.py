import os
import ssl
import json
import smtplib
import requests
import pandas as pd
from datetime import datetime
from datetime import timedelta


# Read configuration variables
config = json.load(open('config.json'))

# API base url
base_url = config['base_url']

# Get authentication token
endpoint = 'api/v1/auth/user/signin'
url = os.path.join(base_url, endpoint)
payload = {
    'email': config['email'],
    'password': config['password']
}
r = requests.post(url, params=payload)
token = r.json()['token']

# Header for new requests
headers = {
    'accept': 'application/json',
    'xc-auth': token
}

# Get project ID, now it basically takes the ID of the first project
endpoint = 'api/v1/db/meta/projects'
url = os.path.join(base_url, endpoint)
r = requests.get(url, headers=headers)
content = r.json()['list'][0]
project_id = content['id']

endpoint = f'api/v1/db/meta/projects/{project_id}/tables'
url = os.path.join(base_url, endpoint)
r = requests.get(url, headers=headers)
data = r.json()['list']
tables = [table['title'] for table in data]

n = 0
for tableName in tables:
    endpoint = f'api/v1/db/data/v1/EPND-glossary/{tableName}'
    url = os.path.join(base_url, endpoint)
    payload = {'limit': 1000}
    r = requests.get(url, headers=headers, params=payload)
    data = r.json()['list']
    print(tableName)
    for row in data:
        if ('Comments' in row.keys()) and (row['Comments'] != ''):
            if row['Comments'] is not None:
                print(row)
                n += 1
    print()
print(f'Total comments {n}')

