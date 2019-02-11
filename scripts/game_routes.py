from flask import Blueprint, request, Response
import cloudsql
import requests as r
from firebase_admin import messaging

# Routes for Hangman game

game = Blueprint('Game', __name__)


# --------------ANDROID-TO-PEPPER-GAME-ROUTES----------------

def relay_to_pepper():
    try:
        content = request.json
        pep_id = content.pop('pep_id')
    except KeyError:
        print ("Missing Data")
        return Response(status=400)

    if request.path == '/startgame':
        # Update FBToken for User in Database.
        try:
            username = content['android_username']
            FBToken = content.pop('FBToken')
        except KeyError:
            return Response(status=400)

        user_query = cloudsql.read('User', username)
        if user_query is None:
            return Response(status=409)

        updates = {'FBToken': FBToken}
        cloudsql.update(user_query, updates)

    pepper = cloudsql.read('Pepper', pep_id)
    if pepper is None:
        return Response(status=406)

    # Check if Pepper is Active
    if pepper.ip_address == '':
        return Response(status=410)

    relay_ip = "http://" + pepper.ip_address + ":8080"

    # Send to Pepper App
    try:
        req = r.post(relay_ip + request.path, json=content)
    except r.exceptions.ConnectionError:
        updates = {'ip_address': ''}
        cloudsql.update(pepper, updates)
        return Response(status=410)

    return Response(status=req.status_code)


game.add_url_rule('/startgame', 'Start', relay_to_pepper, methods=['POST'])
game.add_url_rule('/sendresults', 'Results', relay_to_pepper, methods=['POST'])
game.add_url_rule('/pepperanimation', 'PepperAnimation', relay_to_pepper, methods=['POST'])


# --------------PEPPER-TO-ANDROID-GAME-ROUTES----------------


def relay_to_android():
    try:
        content = request.json
        username = content.pop('android_username')
    except KeyError:
        print ("Missing Data")
        return Response(status=400)

    content.update({'path': request.path[1:]})

    # Find User from Database
    user_query = cloudsql.read('User', username)
    if user_query is None:
        return Response(status=409)

    fb_message = messaging.Message(
        data=content,
        token=user_query.FBToken,
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