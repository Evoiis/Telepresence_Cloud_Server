from scripts import game_routes, pepper_routes, android_routes
from scripts import cloudsql, authentication

from flask import Flask, request, jsonify, Response
from werkzeug.security import generate_password_hash, check_password_hash
import config
import firebase_admin
from firebase_admin import credentials

# Definitions:
# ASK = Android Security Key
# PSK = Pepper Security Key
# FBToken = Firebase Token

app = Flask(__name__)
app.register_blueprint(game_routes.game)
app.register_blueprint(pepper_routes.pepper_routes)
app.register_blueprint(android_routes.android_routes)

app.config.from_object(config)

# Local Instance:
# cred = credentials.Certificate('<Path to JSON credentials file>')
# default_app = firebase_admin.initialize_app(cred)

# GCloud Instance:
default_app = firebase_admin.initialize_app()

# ---------------------------USER-MODEL-ROUTES------------------------


# Login Function for both Pepper App and Android
def login():
    try:
        content = request.json
        username = content['username']
        password = content['password']
    except KeyError:
        print ("Missing Data")
        return Response(status=400)

    # Check for FireBaseToken
    if 'FBToken' in content:
        FBToken = content['FBToken']
    else:
        FBToken = False

    # Check if login coming from Pepper App
    if request.path == '/pepperLogin':
        try:
            pep_id = content['pep_id']
        except KeyError:
            print ("Missing Data")
            return Response(status=400)
        pepper_login = True
    else:
        pepper_login = False

    # Query Database for User
    user_query = cloudsql.read('User', username)
    if user_query is None:
        return Response(status=409)

    # Check if password matches
    if check_password_hash(user_query.password, password):

        # Check if User is authorized for Pepper
        if pepper_login:
            auth_query = cloudsql.read('Auth', (pep_id, username))
            if auth_query is None:
                # User is not authorized for pep_id
                return Response(status=403)
            elif auth_query == -1:
                return Response(status=500)
            elif auth_query.authorized:
                return Response(status=200)
            else:
                return Response(status=403)

        # Get list of authorized Peppers and authorization requests for Android Application
        auth_pepper_list = []
        req_list = []

        key = {'username': username}
        auth_list_query = cloudsql.read_list('Auth', key)

        for auth in auth_list_query:
            if auth.authorized is True:
                    auth_pepper_list.append(auth.pep_id)
            else:
                req_list.append(auth.pep_id)

        # Generate new ASK
        ASK = authentication.generate_random_string()
        hashed_ASK = authentication.hash_ASK(ASK)

        # Update ASK and FBToken in database
        updates = {'ASK': hashed_ASK, 'FBToken': FBToken}
        cloudsql.update(user_query, updates)

        return jsonify(
            {'ASK': hashed_ASK, 'pepper_list': auth_pepper_list, 'request_list': req_list, 'email': user_query.email})
    else:
        return Response(status=401)


app.add_url_rule('/login', 'android_login', login, methods=['POST'])
app.add_url_rule('/pepperLogin', 'pepper_login', login, methods=['POST'])


# Add User record to the database
@app.route('/addUser', methods=['POST'])
def create_user():
    try:
        content = request.json
        username = content['username']
        password = content['password']
        email = content['email']
        name = content['name']
    except KeyError:
        print ("Missing Data")
        return Response(status=400)

    # Generate ASK
    ASK = authentication.generate_random_string()

    # Check if username is already used
    user_query = cloudsql.read('User', username)
    if user_query is not None:
        return Response(status=409)

    # Hash password before saving into database
    hash_pw = generate_password_hash(password)
    new_user = {'username': username, 'password': hash_pw, 'email': email, 'name': name, 'ASK': ASK, 'FBToken': ''}
    cloudsql.create('User', new_user)

    hashed_ASK = authentication.hash_ASK(ASK)
    return jsonify({'ASK': hashed_ASK})


# Used to remove a user from the database
@app.route('/removeUser', methods=['POST'])
def delete_user():
    try:
        content = request.json
        username = content['username']
        password = content['password']
    except KeyError:
        return Response(status=400)

    user_query = cloudsql.read('User', username)
    if user_query is None:
        return Response(status=409)

    if check_password_hash(user_query.password, password):
        cloudsql.delete(user_query)
        return Response(status=200)
    else:
        return Response(status=401)


# ------------------------OTHER-ROUTES---------------------------------------
@app.errorhandler(500)
def server_error():
    return "An internal server error occurred! We all make mistakes but usually it's not me.", 500


# Wipes the database then inserts set of values into the database
@app.route('/testDB', methods=['GET'])
def create_test_set():
    print("Create Test DB")

    cloudsql.wipe_db()
    cloudsql.test_set()

    return 'Database Wiped and replaced with Test Set'


# Wipes the Database
@app.route('/wipeDatabase', methods=['GET'])
def wipe_db():

    cloudsql.wipe_db()
    return 'DB Wiped'


# Show database, used HTML syntax for to make it easy to view in a browser
@app.route('/showDB', methods=['GET'])
def show_db():
    users = cloudsql.read_all('User')
    user_auths = cloudsql.read_all('Auth')
    peppers = cloudsql.read_all('Pepper')

    result = '<h3> Users: </h3><br>'

    for user in users:
        result = result + 'Username: ' + user.username + '| Email: ' + user.email + '| Name: ' + user.name \
                 + '| Password: ' + user.password + '<br>|' + 'FBT: ' + user.FBToken + '<br>|' + 'ASK: ' + user.ASK + '<br><br>'
    result += '<h3> UserAuths: </h3><br>'
    for user_auth in user_auths:
        result = result + 'pep_id: ' + user_auth.pep_id + '| username: ' + user_auth.username + '| email: ' + user_auth.email \
                 + '| Authorized: ' + str(user_auth.authorized) + '<br><br>'
    result += '<h3> Peppers: </h3><br>'
    for pepper in peppers:
        result = result + 'pep_id: ' + pepper.pep_id + '| ip_address: ' + pepper.ip_address + '<br>| PSK: '+ pepper.PSK + '<br><br>'

    return result


if __name__ == '__main__':
    cloudsql.ini_db(app)
    app.run(host='0.0.0.0', port=8080)
