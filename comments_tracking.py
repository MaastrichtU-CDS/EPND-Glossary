# -*- coding: utf-8 -*-

"""
Automation of retrieval of comments and notification of new comments by email
"""

import os
import ssl
import json
import smtplib
import requests
import pandas as pd
from datetime import datetime
from datetime import timedelta
from datetime import timezone


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
# print(f'Project ID: {project_id}')

# Get audit logs for the project and filter only comments
endpoint = f'api/v1/db/meta/projects/{project_id}/audits'
url = os.path.join(base_url, endpoint)
r = requests.get(url, headers=headers)
logs = r.json()['list']
info = r.json()['pageInfo']
rows = info['totalRows'] if info['totalRows'] else info['pageSize']
size = info['pageSize']
df = pd.DataFrame(columns=['User', 'Date', 'Comment', 'fk_model_id', 'row_id'])
for offset in range(0, rows, size):
    for item in logs:
        if item['op_type'] == 'COMMENT':
            df.loc[len(df), df.columns] = \
                item['user'], item['updated_at'], item['description'], \
                    item['fk_model_id'], item['row_id']
    if not r.json()['pageInfo']['isLastPage']:
        payload = {
            'offset': offset + size
        }
        r = requests.get(url, headers=headers, params=payload)
        logs = r.json()['list']
df['Comment'] = \
    df['Comment'].str.replace('The following comment has been created: ', '')

# Filter messages from last 7 days
df['Date'] = df['Date'].apply(pd.to_datetime)
seven_days_ago = datetime.today() - timedelta(days=7)
seven_days_ago = seven_days_ago.replace(tzinfo=timezone.utc).timestamp()
df['timestamp'] = df['Date'].apply(
    lambda x: x.replace(tzinfo=timezone.utc).timestamp()
)
df = df[df['timestamp'] >= seven_days_ago].reset_index()
# print('Comments:')
# print(df.head)

# Get information about the table and row that the comment was made
df['Table'] = ''
df['Row'] = ''
for index, row in df.iterrows():
    fk_model_id = row['fk_model_id']
    row_id = row['row_id']

    # Table information
    endpoint = f'api/v1/db/meta/tables/{fk_model_id}'
    url = os.path.join(base_url, endpoint)
    r = requests.get(url, headers=headers)
    df.loc[index, 'Table'] = r.json()['title']

    # Row information
    endpoint = f'api/v1/db/data/v1/{project_id}/{fk_model_id}/{row_id}'
    url = os.path.join(base_url, endpoint)
    r = requests.get(url, headers=headers)
    df.loc[index, 'Row'] = r.json()['Id']

# Structure comments
df = df[['User', 'Date', 'Table', 'Row', 'Comment']]
comments = f''
for index, row in df.iterrows():
    user = f'User = {row.User}\n'
    date = f'Date = {row.Date}\n'
    table = f'Table = {row.Table}\n'
    item = f'Row = {row.Row}\n'
    comment = f'Comment = {row.Comment}\n\n\n'
    comments += user + date + table + item + comment
comments = 'There were no comments in the past week' if len(comments) == 0 \
    else comments

# Message to be sent via email with weekly comments
message = f"""\
Subject: EPND-glossary weekly comments digest

{comments}"""
message = message.encode('ascii', errors='replace')

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
    # print('Email sent!')
except Exception as e:
    # Print any error messages to stdout
    print(e)
finally:
    server.quit()
