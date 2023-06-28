# -*- coding: utf-8 -*-

"""
Automation of retrieval of comments and notification of new comments for NocoDB
"""

import os
import json
import requests


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

# Get project id, now it basically takes the ID of the first project
endpoint = 'api/v1/db/meta/projects'
url = os.path.join(base_url, endpoint)
r = requests.get(url, headers=headers)
content = r.json()['list'][0]
project_id = content['id']

# Get audit logs for the project and filter only comments
endpoint = f'api/v1/db/meta/projects/{project_id}/audits'
url = os.path.join(base_url, endpoint)
r = requests.get(url, headers=headers)
logs = r.json()['list']
info = r.json()['pageInfo']
rows = info['totalRows']
size = info['pageSize']
for offset in range(0, rows, size):
    for item in logs:
        if item['op_type'] == 'COMMENT':
            print(item['user'])
            print(item['updated_at'])
            print(item['description'])
            print()
    payload = {
        'offset': offset + size
    }
    r = requests.get(url, headers=headers, params=payload)
    logs = r.json()['list']

