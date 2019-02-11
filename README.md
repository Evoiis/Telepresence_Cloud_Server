# Telepresence_Cloud_Server
Cloud Server for Telepresence Software System

Using Google App Engine and Google Cloud SQL, the Telepresence Cloud Server provides a database and serves as a relay between Pepper robots and Android devices.

### Built With
python
Python Flask      -Web Framework
Flask-SQLAlchemy  -Object Relational Mapper for Cloud SQL
Requests          -HTTP Library to send requests
Firebase-admin    -Use Firebase services to send data to Android devices

### Deployment
To setup a local instance of the Cloud Server:
Setup a Google Cloud Platform Account with an App Engine Project and a SQL Database Instance on the Google Cloud Platform
* Google Cloud SDK and Cloud SQL Proxy
* [Google Cloud SDK](https://cloud.google.com/sdk/install)
* [Cloud SQL Proxy](https://cloud.google.com/sql/docs/mysql/sql-proxy)

Using the Google Cloud SDK go to the folder with the cloud_sql_proxy.exe you downloaded </br>
  a. Run a proxy by using the command: cloud_sql_proxy.exe -instances=<PROJECTNAME>=tcp:<PORT> </br>
      (Note: PROJECTNAME should be the “cloud_sql_instances:” value in app.yaml) </br>
* Using a terminal go to the Cloud Server folder from our repository </br>
  a. Run the local instance by using:	python main.py


