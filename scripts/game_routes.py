import cloudsql
import authentication
import requests as req_out
from flask import Blueprint, request, Response, jsonify
from firebase_admin import messaging

# Routes for Hangman game

game = Blueprint('Game', __name__)


# --------------ANDROID-TO-PEPPER-ROUTES----------------

def relay_to_pepper():
    try:
        content = request.json
        if content is None:
            return Response(status=400)

        pep_id = content.pop('pep_id')
        username = content['android_username']
        ASK = content.pop('ASK')
    except KeyError:
        return Response(status=400)

    # Check Android Security Key to authenticate request
    check = authentication.check_ASK(ASK, username)
    if check is None or check is False:
        return Response(status=403)

    if request.path == '/startgame':
        # Update FBToken for User in Database.
        try:
            FBToken = content.pop('FBToken')
        except KeyError:
            return Response(status=400)

        user_query = cloudsql.read('User', username)
        if user_query is None:
            return Response(status=409)

        record_updates = {'FBToken': FBToken}
        cloudsql.update(user_query, record_updates)

    pepper = cloudsql.read('Pepper', pep_id)
    if pepper is None:
        return Response(status=406)

    # Check if Pepper is Active
    if pepper.ip_address == '':
        return Response(status=410)

    relay_ip = "http://" + pepper.ip_address + ":8080"

    # Send request to Pepper App
    try:
        req = req_out.post(relay_ip + request.path + "PEPPER", json=content)
    except req_out.exceptions.ConnectionError:
        record_updates = {'ip_address': ''}
        cloudsql.update(pepper, record_updates)
        return Response(status=410)

    return Response(status=req.status_code)


game.add_url_rule('/startgame', 'Start', relay_to_pepper, methods=['POST'])
game.add_url_rule('/sendresults', 'Results', relay_to_pepper, methods=['POST'])
game.add_url_rule('/pepperanimation', 'PepperAnimation', relay_to_pepper, methods=['POST'])


# --------------PEPPER-TO-ANDROID-ROUTES----------------


def relay_to_android():
    try:
        content = request.json
        if content is None:
            return Response(status=400)

        username = content['android_username']
        pep_id = content['pep_id']
        PSK = content['PSK']
    except KeyError:
        return Response(status=400)

    content.update({'path': request.path[1:]})

    check_result = authentication.check_PSK(PSK, pep_id)
    if check_result is None:
        return jsonify({'Error': "pep_id not found."}), 409
    elif check_result is False:
        return Response(status=403)

    # Find User from Database
    user_query = cloudsql.read('User', username)
    if user_query is None:
        return jsonify({'Error': "User not found."}), 409

    # Create Firebase Message object
    fb_message = messaging.Message(
        data=content,
        token=user_query.FBToken,   # Defines the Android app instance to send the message to
    )
    try:
        response = messaging.send(fb_message)
    except:
        print ("Message failed to send.")
        return Response(status=410)
    return Response(status=200)


game.add_url_rule('/acceptgame', 'Accept', relay_to_android, methods=['POST'])
game.add_url_rule('/endgame', 'End', relay_to_android, methods=['POST'])
game.add_url_rule('/androidanimation', 'AndroidAnimation', relay_to_android, methods=['POST'])
game.add_url_rule('/deny', 'Deny', relay_to_android, methods=['POST'])