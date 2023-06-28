# -*- coding: utf-8 -*-

"""
Automation of retrieval of comments and notification of new comments for NocoDB
"""

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
df = pd.DataFrame(columns=['User', 'Date', 'Comment'])
for offset in range(0, rows, size):
    for item in logs:
        if item['op_type'] == 'COMMENT':
            df.loc[len(df), df.columns] = \
                item['user'], item['updated_at'], item['description']
    payload = {
        'offset': offset + size
    }
    r = requests.get(url, headers=headers, params=payload)
    logs = r.json()['list']

# Filter messages from last 7 days
df['Date'] = df['Date'].apply(pd.to_datetime)
seven_days_ago = datetime.today() - timedelta(days=7)
df_tmp = df[df['Date'] >= seven_days_ago]

# Message to be sent via email with weekly comments
message = f"""\
Subject: EPND-glossary comments

Weekly comments digest
{df}
"""

# SMTP configuration
smtp_server = config['smtp_server']
port = config['smtp_port']
sender = config['smtp_sender']
password = config['smtp_pass']
receiver = config['receiver']

# Create a secure SSL context
context = ssl.create_default_context()

# Try to log in to SMTP server and send email
try:
    server = smtplib.SMTP(smtp_server, port)
    server.ehlo()
    server.starttls(context=context)
    server.ehlo()
    server.login(sender, password)
    server.sendmail(sender, receiver, message)
except Exception as e:
    # Print any error messages to stdout
    print(e)
finally:
    server.quit()
