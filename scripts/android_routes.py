import cloudsql
import authentication
import json
import requests as req_out
from flask import Blueprint, request, Response, jsonify

# Routes for requests sent exclusively from Android to Cloud Server

android_routes = Blueprint('Android', __name__)


# Used to relay a message from Android and send back a response from Pepper
@android_routes.route('/message', methods=['POST'])
def message():
    try:
        content = request.json
        username = content['username']
        pep_id = content['pep_id']
        ASK = content['ASK']
        msg = content['message']
    except KeyError:
        return Response(status=400)

    # Check Android Security Key to authenticate request
    check = authentication.check_ASK(ASK, username)
    if check is None or check is False:
        return Response(status=403)

    # Check if user is authorized for pep_id
    auth_query = cloudsql.read('Auth', (pep_id, username))
    if auth_query is None:
        return Response(status=401)
    elif not auth_query.authorized:
        return Response(status=401)
    elif auth_query == -1:
        return Response(status=500)

    # Check if pep_id is registered.
    pepper = cloudsql.read('Pepper', pep_id)
    if pepper is None:
        # pep_id is not registered
        return Response(status=409)
    elif auth_query == -1:
        return Response(status=500)

    # Check if Pepper App is active
    if pepper.ip_address == '':
        return jsonify({'Error': "Pepper Application is inactive."}), 410

    relay_ip = "http://" + pepper.ip_address + ":8080/message"

    # Hash PSK from database
    new_PSK = authentication.hash_PSK(pepper.PSK)

    try:
        # Send request to Pepper
        req = req_out.post(relay_ip, data=json.dumps({'msg': msg, 'PSK': new_PSK, 'username': username}))
    except req_out.exceptions.ConnectionError as error:
        # Set Pepper record to inactive
        record_updates = {'ip_address': ''}
        cloudsql.update(pepper, record_updates)
        return jsonify({'Error': "Pepper failed to respond."}), 410

    if req.status_code == 200:
        # Update PSK in database
        record_updates = {'PSK': new_PSK}
        cloudsql.update(pepper, record_updates)
        return req.text

    else:
        return Response(status=req.status_code)


# Relays photo from Android to Pepper
@android_routes.route('/photo', methods=['POST'])
def photo():
    try:
        content = request.form
        username = content['username']
        pep_id = content['pep_id']
        ASK = content['ASK']
        photo_file = request.files['file']
    except KeyError:
        return Response(status=400)

    # Read file content and encode photo into base64 string.
    file_content = photo_file.read()
    encoded_photo = file_content.encode('base64')

    # Check Android Security Key to authenticate request.
    check = authentication.check_ASK(ASK, username)
    if check is None or check is False:
        return Response(status=403)

    # Check if user is authorized for pep_id.
    auth_query = cloudsql.read('Auth', (pep_id, username))
    if auth_query is None:
        return Response(status=401)
    elif not auth_query.authorized:
        return Response(status=401)
    elif auth_query == -1:
        return Response(status=500)

    # Check if pep_id is registered.
    pepper = cloudsql.read('Pepper', pep_id)
    if pepper is None:
        return Response(status=409)
    elif pepper == -1:
        return Response(status=500)

    # Check if Pepper is Active.
    if pepper.ip_address == '':
        return jsonify({'Error': "Pepper Application is inactive."}), 410

    relay_ip = "http://" + pepper.ip_address + ":8080/photo"
    print("Sending photo to: " + relay_ip)

    # Hash PSK from database
    new_PSK = authentication.hash_PSK(pepper.PSK)

    try:
        req = req_out.post(relay_ip, json={'PSK': new_PSK, 'photo': encoded_photo})
    except req_out.exceptions.ConnectionError:
        # Set Pepper record to inactive.
        record_updates = {'ip_address': ''}
        cloudsql.update(pepper, record_updates)
        return jsonify({'Error': "Pepper failed to respond."}), 410

    if req.status_code == 200:
        # Update PSK in database
        record_updates = {'PSK': new_PSK}
        cloudsql.update(pepper, record_updates)
        return req.text
    else:
        return Response(status=200)


# Create new authorization request and add to database
@android_routes.route('/reqAuth', methods=['POST'])
def request_auth():
    try:
        content = request.json
        pep_id = content['pep_id']
        username = content['username']
        email = content['email']
        ASK = content['ASK']
    except KeyError:
        return Response(status=400)

    # Check Android Security Key to authenticate request.
    check = authentication.check_ASK(ASK, username)
    if check is None or check is False:
        return Response(status=403)

    # Check if pep_id is registered.
    pepper = cloudsql.read('Pepper', pep_id)
    if pepper is None:
        return Response(status=409)
    elif pepper == -1:
        return Response(status=500)

    new_request = {'pep_id': pep_id, 'username': username, 'email': email, 'authorized': False}
    cloudsql.create('Auth', new_request)

    return Response(status=200)
