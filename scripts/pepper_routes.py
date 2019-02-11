import cloudsql
import authentication
from flask import Blueprint, request, Response, jsonify
from firebase_admin import messaging

# Routes for requests sent exclusively from Pepper to Cloud Server.

pepper_routes = Blueprint('Pepper', __name__)


# Deletes an user authorization record.
@pepper_routes.route('/deAuth', methods=['POST'])
def deauthorize():
    try:
        content = request.json
        pep_id = content['pep_id']
        PSK = content['PSK']
        username = content['username']
    except KeyError:
        return Response(status=400)

    check_result = authentication.check_PSK(PSK, pep_id)
    if check_result is None:
        return jsonify({'Error': "pep_id not found."}), 409
    elif check_result is False:
        return Response(status=403)

    auth_query = cloudsql.read('Auth', (pep_id, username))
    if auth_query is None:
        return jsonify({'Error': "User Authorization not found."}), 409
    elif auth_query == -1:
        return Response(status=500)

    cloudsql.delete(auth_query)

    return Response(status=200)


# Finds list of username and email tuples associated with a pep_id.
def find_user_auths():
    try:
        content = request.json
        pep_id = content['pep_id']
        PSK = content['PSK']
    except KeyError:
        print ("Missing Data")
        return Response(status=400)

    check_result = authentication.check_PSK(PSK, pep_id)
    if check_result is None:
        return Response(status=409)
    elif check_result is False:
        return Response(status=403)

    result_list = []

    # Check if we are getting authorized users and users requesting authorization.
    if request.path == '/getAuthUsers':
        get_authorized = True
    else:
        get_authorized = False

    key = {'pep_id': pep_id}
    auth_list_query = cloudsql.read_list('Auth', key)
    if auth_list_query == -1:
        return Response(status=500)

    for auth_req in auth_list_query:
        if auth_req.authorized is get_authorized:
            result_list.append((auth_req.username, auth_req.email))

    if get_authorized:
        return jsonify({'AuthUsers': result_list})
    else:
        return jsonify({'AuthReqs': result_list})


pepper_routes.add_url_rule('/getAuthRequests', 'list_Authorization_Requests', find_user_auths, methods=['POST'])
pepper_routes.add_url_rule('/getAuthUsers', 'list_Authorized_Users', find_user_auths, methods=['POST'])


# Authorizes a user for a pep_id by updating the corresponding UserAuth record
@pepper_routes.route('/authorizeUser', methods=['POST'])
def authorizeUser():
    try:
        content = request.json
        pep_id = content['pep_id']
        PSK = content['PSK']
        username = content['username']
    except KeyError:
        return Response(status=400)

    check_result = authentication.check_PSK(PSK, pep_id)
    if check_result is None:
        return jsonify({'Error': "pep_id not found."}), 409
    elif check_result is False:
        return Response(status=403)

    user_query = cloudsql.read('User', username)
    if user_query is None:
        return jsonify({'Error': "User not found."}), 409
    elif user_query == -1:
        return Response(status=500)

    auth_query = cloudsql.read('Auth', (pep_id, username))
    if auth_query is None:
        # UserAuth does not exist, so add a new one and authorize
        new_auth = {'username': username, 'pep_id': pep_id, 'email': user_query.email, 'authorized': True}
        cloudsql.create('Auth', new_auth)
    elif auth_query == -1:
        return Response(status=500)

    record_updates = {'authorized': True}
    cloudsql.update(auth_query, record_updates)

    return Response(status=200)


# Add or update a Pepper record.
@pepper_routes.route('/addPepper', methods=['POST'])
def add_update_Pepper():
    try:
        content = request.json
        pep_id = content['pep_id']
        ip = request.access_route[0]
        PSK = content['PSK']
        username = content['username']
    except KeyError:
        print ("Missing Data")
        return Response(status=400)

    # Pepper App will send in a non-empty username when in first-time setup mode
    if username != '':
        user_query = cloudsql.read('User', username)
        if user_query is None:
            return jsonify({'Error': "User not found."}), 410
        elif user_query == -1:
            return Response(status=500)

    # Check for existing Pepper entity with pep_id.
    pepper = cloudsql.read('Pepper', pep_id)
    if pepper == -1:
        return Response(status=500)

    if pepper is None:
        if username == '':
            # Pepper App has pep_id registered when database does not, send 410 to notify
            return jsonify({'Error': "Pepper not found. Please register again."}), 410

        # Register new Pepper into database
        new_pepper = {'pep_id': pep_id, 'ip_address': ip, 'PSK': PSK}
        cloudsql.create('Pepper', new_pepper)

        # Check database for any existing UserAuth records
        key = {'pep_id': pep_id}
        auth_list_query = cloudsql.read_list('Auth', key)
        if auth_list_query == -1:
            return Response(status=500)

        # Delete all of them to guarantee correct authorization
        for auth in auth_list_query:
            cloudsql.delete(auth)

        # Authorize user that is registering new Pepper
        new_user_auth = {'pep_id': pep_id, 'username': username, 'email': user_query.email, 'authorized': True}
        cloudsql.create('Auth', new_user_auth)

        return Response(status=200)
    else:
        if username != '':
            # pep_id is already in use in database, send 409 to notify Pepper App to tell user to choose another one
            return Response(status=409)

        # Pepper already exists so update database record
        record_updates = {'ip_address': ip, 'PSK': PSK}
        cloudsql.update(pepper, record_updates)

        return Response(status=200)


# Proactive notifications = Notifications sent to Android when certain events hpepper_routesen to Pepper
# Ex: Person touches Pepper's head
# Proactive notification from Pepper to Android
@pepper_routes.route('/proactive', methods=['POST'])
def proactive():
    try:
        content = request.json
        message = content['msg']
        PSK = content.pop('PSK')
        username = content.pop('android_username')
        pep_id = content.pop('pep_id')
    except KeyError:
        print ("Missing Data")
        return Response(status=400)

    # Add path to content for Android App.
    content.update({'path': request.path[1:]})

    check_result = authentication.check_PSK(PSK, pep_id)
    if check_result is None:
        return Response(status=409)
    elif check_result is False:
        return Response(status=403)

    # Find User from Database
    user_query = cloudsql.read('User', username)

    if user_query is None:
        return Response(status=409)
    if user_query == -1:
        return Response(status=500)

    notification = messaging.Notification("Pepper Alert!", message)

    # Create Firebase Message object
    fb_message = messaging.Message(
        data=content,
        notification=notification,
        token=user_query.FBToken,       # Defines the Android app instance to send the message to
    )

    # Send to Android App
    try:
        response = messaging.send(fb_message)
    except:
        print ("Message failed to send.")
        return Response(status=410)
    return Response(status=200)