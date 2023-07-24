# EPND glossary

This glossary was developed to enable transdisciplinary collaboration 
within the [European Platform for Neurodegenerative Diseases](https://epnd.org)
(EPND) project, which requires heterogeneous partners (e.g., researchers, 
regulators, legal experts) and competencies (e.g., technical, academic,
industry, etc.) in the field of neurodegenerative disorders.

The collaborative EPND glossary was created using the open source platform 
[NocoDB](https://nocodb.com) and deployed as a Web App in the Azure cloud. 
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

The glossary was deployed in the Azure cloud, following the user's 
[documentation](https://docs.nocodb.com/getting-started/installation/) with 
the necessary changes for Azure deployment. Below is a summary of the process
using the Azure client.

1. Login to Azure
``` bash
az login
```

2. Create a resource group
``` bash
az group create --name <group> \
                --location westeurope
```
where `<group>` is the desired name for your resource group, which is deployed
in West Europe

3. Create an app service plan
``` bash
az appservice plan create --resource-group <group> \
                          --name <service-plan> \
                          --location westeurope \
                          --sku B2 --is-linux
```
where `<service-plan>` is the name you wish to give to your service plan, with a
pricing plan `B2`

4. Deploy NocoDB as a web app in the app service plan                          
``` bash
az webapp create --resource-group <group> \
                 --plan <service-plan> \
                 --name <web-address> \
                 -i registry.hub.docker.com/nocodb/nocodb:latest
```
where `<web-address>` is the name you wish to give to your web app, if
`<web-address>` is `nocodb-test`, you will be able to access the web app at
`http://nocodb-test.azurewebsites.net/dashboard`, here we also use the latest
NocoDB image from Docker Hub

5. Configure the web app to send requests to port 8080
``` bash
az webapp config appsettings set --resource-group <group> \
								 --name <web-address> \
								 --settings WEBSITES_PORT=8080
```

6. Create a storage account for persistent storage to prevent data loss
``` bash
az storage account create --name <storage-name> \
                          --resource-group <group> \
						  --location westeurope \
						  --sku Standard_RAGRS --https-only
```
where `<storage-name>` is the name you wish to give for the storage account

7. Create an Azure file share for the web app container
``` bash
az storage share-rm create --resource-group <group> \
	                       --storage-account <storage-name> \
						   --name <share-name>
```
where `<share-name>` is the name id for the file share

8. Get the access key for your storage account, which will you need in step 9
``` bash
az storage account keys list --resource-group <group> \
                             --account-name <storage-name>
```

9. Add a storage mount for the file share
``` bash
az webapp config storage-account add --resource-group <group> \
                                     --name <web-address> \
  								     --storage-type AzureFiles \
  								     --account-name <storage-name> \
  								     --share-name <share-name> \
  								     --mount-path /usr/app/data \
  								     --slot-setting True \
  								     --custom-id <webapp-storage> \
  								     --access-key <key>
```
where `<webapp-storage>` is a custom name given for the share configured within
the web app, `--mount-path` is the path with the web app data, and `<key>` is
the key retrieved in step 8

10. Open the web app in your browser to test the deployment
``` bash
az webapp browse --resource-group <group> \
                 --name <web-address>
```	

11. If you wish to delete all resources run the following
``` bash
az group delete --name <group>
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

1. Install dependencies (tested in Python 3.10), it is a good idea to create a
   virtual environment for the project
``` bash
pip install -r requirements.txt
```

2. Create the `config.json` input
``` bash
cp config.json.example config.json
```

3. Open the `config.json` file and edit it accordingly

4. Run the script to get comments and send them by email
``` bash
python comments_tracking.py
```

