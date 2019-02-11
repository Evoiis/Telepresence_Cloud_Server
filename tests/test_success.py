import requests
import json
import hashlib
import os


# Hash Functions:
def hash_PSK(key):
    salt = '<Salt String>'
    key += salt
    result = hashlib.sha256(key).hexdigest()
    return result


def hash_ASK(key):
    salt = '<Salt String>'
    key += salt
    key.encode('utf-8')
    result = hashlib.md5(key).hexdigest()
    return result


ip = 'http://localhost:8080'
encrypt_salt = '<Salt String>'
cwd = os.getcwd()

# first and second are 2 User records
first_ASK = ''
second_ASK = ''

# robot and pepper are 2 Pepper records
robot_PSK = 'robot'
pepper_PSK = 'pepper'

# Make sure TESTING_MODE = True in main.py

# Empty database for testing
response = requests.get(ip + '/wipeDatabase')
if response.status_code != 200:
    raise Exception("Database wipe Failed! Check if TESTING_MODE is True in main.py.")

# Delete result photo before sending
if os.path.exists("./photo/received.png"):
    os.remove("./photo/received.png")
    print("File deleted.")
else:
    print("File does not exist.")

# ---------------------------------------------------------------------------------------------
# Add 2 Users:
response = requests.post(ip + '/addUser', json={'username': 'first', 'email': 'first@example.com', 'password': 'first',
                                                'name': 'evoiis'})
if response.status_code != 200:
    raise Exception("Error adding FIRST user to fresh database. " + "Status code = " + str(response.status_code))
first_ASK = json.loads(response.text)['ASK']

response = requests.post(ip + '/addUser',
                         json={'username': 'second', 'email': 'second@example.com', 'password': 'second',
                               'name': 'siiove'})
if response.status_code != 200:
    raise Exception("Error adding SECOND user to fresh database. " + "Status code = " + str(response.status_code))
second_ASK = json.loads(response.text)['ASK']

# ---------------------------------------------------------------------------------------------
# Add 2 Pepper records:
response = requests.post(ip + '/addPepper', json={'pep_id': 'robot', 'PSK': robot_PSK, 'username': 'first'})
if response.status_code != 200:
    raise Exception(
        "Error adding ROBOT record to Database using /addPepper. " + "Status code = " + str(response.status_code))

response = requests.post(ip + '/addPepper', json={'pep_id': 'pepper', 'PSK': pepper_PSK, 'username': 'first'})
if response.status_code != 200:
    raise Exception(
        "Error adding PEPPER record to Database using /addPepper. " + "Status code = " + str(response.status_code))

robot_PSK = hash_PSK(robot_PSK)
pepper_PSK = hash_PSK(pepper_PSK)

# Make 2 UserAuth requests for User SECOND
response = requests.post(ip + '/reqAuth', json={'username': 'second', 'email': 'second@example.com', 'pep_id': 'robot',
                                                'ASK': second_ASK})
if response.status_code != 200:
    raise Exception("Error adding UserAuth for SECOND User for ROBOT" + "Status code = " + str(response.status_code))

second_ASK = hash_ASK(second_ASK)

response = requests.post(ip + '/reqAuth', json={'username': 'second', 'email': 'second@example.com', 'pep_id': 'pepper',
                                                'ASK': second_ASK})
if response.status_code != 200:
    raise Exception("Error adding UserAuth for SECOND User for PEPPER" + "Status code = " + str(response.status_code))

# ---------------------------------------------------------------------------------------------
# Check Auth Requests for ROBOT
response = requests.post(ip + '/getAuthRequests', json={'pep_id': 'robot', 'PSK': robot_PSK})
if response.status_code != 200:
    raise Exception("Error getting AuthRequests for ROBOT" + "Status code = " + str(response.status_code))

robot_auth_reqs = json.loads(response.text)['AuthReqs']
if robot_auth_reqs[0][0] != 'second':
    raise Exception("Unexpected output from /getAuthRequests for ROBOT")

# Check Auth Requests for PEPPER
response = requests.post(ip + '/getAuthRequests', json={'pep_id': 'pepper', 'PSK': pepper_PSK})
if response.status_code != 200:
    raise Exception("Error getting AuthRequests for PEPPER" + "Status code = " + str(response.status_code))

pepper_auth_reqs = json.loads(response.text)['AuthReqs']
if pepper_auth_reqs[0][0] != 'second':
    raise Exception("Unexpected output from /getAuthRequests for PEPPER")

robot_PSK = hash_PSK(robot_PSK)
pepper_PSK = hash_PSK(pepper_PSK)

# ---------------------------------------------------------------------------------------------
# Check Authorized Users for ROBOT
response = requests.post(ip + '/getAuthUsers', json={'pep_id': 'robot', 'PSK': robot_PSK})
if response.status_code != 200:
    raise Exception("Error getting Authorized Users for ROBOT" + "Status code = " + str(response.status_code))

robot_auth_reqs = json.loads(response.text)['AuthUsers']
if robot_auth_reqs[0][0] != 'first':
    raise Exception("Unexpected output from /getAuthUsers for ROBOT")

# Check Authorized Users for pepper
response = requests.post(ip + '/getAuthUsers', json={'pep_id': 'pepper', 'PSK': pepper_PSK})
if response.status_code != 200:
    raise Exception("Error getting Authorized Users for PEPPER" + "Status code = " + str(response.status_code))

pepper_auth_reqs = json.loads(response.text)['AuthUsers']
if pepper_auth_reqs[0][0] != 'first':
    raise Exception("Unexpected output from /getAuthUsers for PEPPER")

robot_PSK = hash_PSK(robot_PSK)
pepper_PSK = hash_PSK(pepper_PSK)

# ---------------------------------------------------------------------------------------------
# AUTHORIZE AND DEAUTHORIZE TEST
# Authorize SECOND for ROBOT
response = requests.post(ip + '/authorizeUser', json={'pep_id': 'robot', 'PSK': robot_PSK, 'username': 'second'})
if response.status_code != 200:
    raise Exception("Error Authorizing SECOND for ROBOT" + "Status code = " + str(response.status_code))

robot_PSK = hash_PSK(robot_PSK)

# Check Authorized Users for ROBOT
response = requests.post(ip + '/getAuthUsers', json={'pep_id': 'robot', 'PSK': robot_PSK})
if response.status_code != 200:
    raise Exception("Error getting Authorized Users for ROBOT" + "Status code = " + str(response.status_code))

robot_auth_reqs = json.loads(response.text)['AuthUsers']
if robot_auth_reqs[0][0] != 'first':
    raise Exception("Unexpected output from /getAuthUsers for ROBOT")
if robot_auth_reqs[1][0] != 'second':
    raise Exception("Unexpected output from /getAuthUsers for ROBOT")

robot_PSK = hash_PSK(robot_PSK)

# Deauthorize FIRST for ROBOT
response = requests.post(ip + '/deAuth', json={'username': 'first', 'pep_id': 'robot', 'PSK': robot_PSK})
if response.status_code != 200:
    raise Exception("Error deauthorizing FIRST for ROBOT" + "Status code = " + str(response.status_code))

robot_PSK = hash_PSK(robot_PSK)

# Check Authorized Users for ROBOT
response = requests.post(ip + '/getAuthUsers', json={'pep_id': 'robot', 'PSK': robot_PSK})
if response.status_code != 200:
    raise Exception("Error getting Authorized Users for ROBOT" + "Status code = " + str(response.status_code))

robot_auth_reqs = json.loads(response.text)['AuthUsers']
if robot_auth_reqs[0][0] != 'second':
    raise Exception("Unexpected output from /getAuthUsers for ROBOT")

try:
    deleted = robot_auth_reqs[1][0]
    raise Exception("Unexpected output from /getAuthUsers for ROBOT")
except IndexError:
    robot_PSK = hash_PSK(robot_PSK)

# ---------------------------------------------------------------------------------------------
# Send message from FIRST to mock pepper server
response = requests.post(ip + '/message', json={'username': 'first', 'pep_id': 'pepper', 'ASK': first_ASK,
                                                'message': 'Hello Mock Pepper!'})
if response.text != "0":
    raise Exception("Error sending message to PEPPER from FIRST" + "Status code = " + str(response.status_code))

first_ASK = hash_ASK(first_ASK)

# Send /startgame from FIRST to mock pepper server
response = requests.post(ip + '/startgame', json={'android_username': 'first', 'hint': 'fake_hint', 'word': 'fake_word',
                                                  'pep_id': 'pepper', 'FBToken': '', 'ASK': first_ASK})
if response.status_code != 200:
    raise Exception("Error sending /startgame to PEPPER from FIRST" + "Status code = " + str(response.status_code))

first_ASK = hash_ASK(first_ASK)

# Send /sendresults from FIRST to mock pepper server
response = requests.post(ip + '/sendresults',
                         json={'android_username': 'first', 'time_taken': 'fake_time', 'lives_left': 'fake_lives',
                               'pep_id': 'pepper', 'ASK': first_ASK})
if response.status_code != 200:
    raise Exception("Error sending /sendresults to PEPPER from FIRST" + "Status code = " + str(response.status_code))

first_ASK = hash_ASK(first_ASK)

# Send /pepperanimation from FIRST to mock pepper server
response = requests.post(ip + '/pepperanimation',
                         json={'android_username': 'first', 'animation': 'fake_animation', 'pep_id': 'pepper',
                               'ASK': first_ASK})
if response.status_code != 200:
    raise Exception(
        "Error sending /pepperanimation to PEPPER from FIRST" + "Status code = " + str(response.status_code))

first_ASK = hash_ASK(first_ASK)

# Send photo from FIRST to mock pepper server
test_json = {'username': 'first', 'pep_id': 'pepper', 'ASK': first_ASK}
response = requests.post(ip + '/photo', data=test_json, files={'file': ('test.png', open(cwd + '\\test.png', 'rb'))})
if response.status_code == 200:
    print("Check int /tests/photo for received.png. Should match test.png in /tests")
else:
    raise Exception("Error sending /photo to PEPPER from FIRST" + "Status code = " + str(response.status_code))

# ---------------------------------------------------------------------------------------------
# Login as SECOND User
response = requests.post(ip + '/login', json={'username': 'first', 'password': 'first', 'FBToken': ''})
if response.status_code != 200:
    raise Exception("Error /login as FIRST" + "Status code = " + str(response.status_code))

first_ASK = json.loads(response.text)['ASK']

# Delete SECOND User
response = requests.post(ip + '/removeUser', json={'username': 'second', 'password': 'second'})
if response.status_code != 200:
    raise Exception("Error /removeUser as SECOND" + "Status code = " + str(response.status_code))
else:
    print("Check localhost:8080/showDB for no SECOND user and no UserAuths for SECOND")
