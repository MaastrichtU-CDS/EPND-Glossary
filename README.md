# EPND glossary

This glossary was developed to enable transdisciplinary collaboration 
within the [European Platform for Neurodegenerative Diseases](https://epnd.org)
(EPND) project, which requires heterogeneous partners (e.g., researchers, 
regulators, legal experts) and competencies (e.g., technical, academic,
industry, etc.) in the field of neurodegenerative disorders.

The collaborative EPND glossary was created using the open source platform 
[NocoDB](https://nocodb.com) and deployed as a Web App on the Azure cloud. 
The power of NocoDB, and reason for which it was chosen, is the fact that it 
can connect to any relational database and convert it into a collaborative 
spreadsheet with a user-friendly interface. Users can simultaneously work on 
tables, change views, and comment on the content, with an audit process 
that tracks all operations on the system. Furthermore, REST APIs are 
provided to interact with the database and perform task automation, which 
can help with the management of the glossary. NocoDB allowed to create a 
modular glossary organised by themes. Each module was structured as a table 
defining terms, their definitions, and references related to them.

The most challenge part of establishing a glossary is achieving convergence 
on the terms' definitions. In the EPND glossary, we took a Wiki-like approach, 
where certain participants were given an editor role and could freely define 
and revise terms related to their expertise. Another group of participants 
were given a commenter role and used to further peer-review the defined terms. 
This workflow enabled the development of a dynamic glossary that can quickly 
adapt. A public view of the [EPND glossary](https://epnd-glossary.azurewebsites.net/dashboard/#/base/c061cde8-1afa-45aa-bee8-3a689e9c518c) 
is published online and can be freely consulted.

## Deployment

The glossary was deployed on the Azure cloud, following the user's 
[documentation](https://docs.nocodb.com/getting-started/installation/) with 
minor changes. Below is a summary of the process using the Azure client.

``` bash
    # Create an App Service plan
    $ az appservice plan create -g <GROUP> \
                                -n <SERVICE_PLAN_NAME> \
                                -l westeurope \
                                --sku B1 --is-linux
                              
    # Deploy NocoDB as a Web App in the App Service plan                          
    $ az webapp create -g <GROUP> \
                       -p <SERVICE_PLAN_NAME> \
                       -n <WEB_ADDRESS> \
                       -i nocodb/nocodb:latest
```

## Glossary creation

The glossary was created using the web interface. Each module is a different 
table, where the columns are the necessary elements to properly define its 
modules' terms and each row is a different term.

## Comments tracking

The comment feature of NocoDB was used to help discussion about the terms and 
facilitate the review process of the definitions. Comment tracking was 
automated with a combination of comments' retrieval using the REST APIs and 
notification of the new comments via email using the `comments_tracking.py` 
script. A crontab job was scheduled to automatically run the script and 
moderators got notified of the comments with the desired frequency.

The `config.json.example` has an example of the necessary input to run the
script. Below is a summary of how this script should be run.

``` bash
	# Install dependencies (tested in Python 3.10)
	$ pip install -r requirements.txt
	
	# Create config.json input, open the file, and edit it accordingly
	$ cp config.json.example config.json
	
	# Get comments and send them by email
	$ python comments_tracking.py
```

