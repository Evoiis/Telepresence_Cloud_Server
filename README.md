# Telepresence_Cloud_Server
Cloud Server for Telepresence Software System

Using Google App Engine and Google Cloud SQL, the Telepresence Cloud Server provides access to a database and relays data between Pepper robots and Android devices.

### Built With
* Python
* Python Flask      -Web Framework
* Flask-SQLAlchemy  -Object Relational Mapper for Cloud SQL
* Requests          -HTTP Library to send requests to Pepper robots
* Firebase-admin    -Use Firebase services to send data to Android devices

## Telepresence System Architecture
<img width="1052" alt="screen shot 2018-11-13 at 7 29 24 pm" src="https://user-images.githubusercontent.com/34588197/48458275-7fbe3b80-e77a-11e8-9f69-00dcce7f954d.png"/></br>

### Testing with test_success.py
* Set TESTING_MODE to True in main.py
* Start Local Instance
* Run test_success with: python test_success.py
