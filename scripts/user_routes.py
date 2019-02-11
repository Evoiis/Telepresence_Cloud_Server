import cloudsql
import authentication
from flask import Blueprint, request, Response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# Routes specifically for reading, creating, deleting User records in database

user_routes = Blueprint('User', __name__)


# Login Function for both Pepper App and Android
def login():
    try:
        content = request.json
        if content is None:
            return Response(status=400)

        username = content['username']
        password = content['password']
    except KeyError:
        # Missing Data in request json
        return Response(status=400)

    # Check for FireBaseToken
    if 'FBToken' in content:
        FBToken = content['FBToken']
    else:
        FBToken = False

    # Check if login is coming from Pepper App.
    if request.path == '/pepperLogin':
        try:
            pep_id = content['pep_id']
        except KeyError:
            # Missing Data in request json
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
        record_updates = {'ASK': hashed_ASK, 'FBToken': FBToken}
        cloudsql.update(user_query, record_updates)

        return jsonify(
            {'ASK': hashed_ASK, 'pepper_list': auth_pepper_list, 'request_list': req_list, 'email': user_query.email})
    else:
        return Response(status=401)


user_routes.add_url_rule('/login', 'android_login', login, methods=['POST'])
user_routes.add_url_rule('/pepperLogin', 'pepper_login', login, methods=['POST'])


# Add User record to the database
@user_routes.route('/addUser', methods=['POST'])
def create_user():
    try:
        content = request.json
        if content is None:
            return Response(status=400)

        username = content['username']
        password = content['password']
        email = content['email']
        name = content['name']
    except KeyError:
        # Missing Data in request json
        return Response(status=400)

    # Check if username is already used
    user_query = cloudsql.read('User', username)
    if user_query is not None:
        return Response(status=409)

    # Generate Android Security Key
    ASK = authentication.generate_random_string()

    # Hash user password before saving into database
    hash_pw = generate_password_hash(password)
    new_user = {'username': username, 'password': hash_pw, 'email': email, 'name': name, 'ASK': ASK, 'FBToken': ''}
    cloudsql.create('User', new_user)

    hashed_ASK = authentication.hash_ASK(ASK)
    return jsonify({'ASK': hashed_ASK})


# Used to remove a user from the database
@user_routes.route('/removeUser', methods=['POST'])
def delete_user():
    try:
        content = request.json
        if content is None:
            return Response(status=400)

        username = content['username']
        password = content['password']
    except KeyError:
        return Response(status=400)

    user_query = cloudsql.read('User', username)
    if user_query is None:
        return Response(status=409)

    # Check password before deleting
    if check_password_hash(user_query.password, password):
        cloudsql.delete(user_query)

        # Check database for any existing UserAuth records
        key = {'username': username}
        auth_list_query = cloudsql.read_list('Auth', key)
        if auth_list_query == -1:
            return Response(status=500)

        # Delete all of them to guarantee correct authorization
        for auth in auth_list_query:
            cloudsql.delete(auth)

        return Response(status=200)
    else:
        return Response(status=401)
