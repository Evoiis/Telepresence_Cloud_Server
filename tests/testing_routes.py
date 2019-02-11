from scripts import cloudsql
from flask import Blueprint, request, Response
# Flask Routes for Testing

testing_routes = Blueprint('Test', __name__)


# Mock Pepper Server:

@testing_routes.route('/PepperMessage', methods=['POST'])
def receive_message():
    try:
        content = request.json
        if content is None:
            print("MOCK PEPPER: Error! Empty JSON in message")
            return "1"

        message = content['msg']
    except KeyError:
        print("MOCK PEPPER: Error! Missing message!")
        return "1"

    print("MOCK PEPPER: Message received = " + message)

    return "0"


@testing_routes.route('/PepperPhoto', methods=['POST'])
def receive_photo():
    try:
        content = request.json
        if content is None:
            print("MOCK PEPPER: Error! Empty JSON in photo")
            return "1"

        photo = content['photo']
    except KeyError:
        print("MOCK PEPPER: Error! Missing photo!")
        return "1"

    photo_file = photo.decode('base64')
    save_file = open('.\\tests\\photo\\received.png', 'wb')
    save_file.write(photo_file)
    save_file.close()
    # print("MOCK PEPPER: Photo received = " + photo)

    return "0"


@testing_routes.route('/startgamePEPPER', methods=['POST'])
def receive_startgame():
    try:
        content = request.json
        if content is None:
            print("MOCK PEPPER: Error! Empty JSON in startgame")
            return "1"

        username = content['android_username']
        hint = content['hint']
        word = content['word']
    except KeyError:
        print("MOCK PEPPER: Error! Missing username,hint,or word!")
        return "1"

    print("MOCK PEPPER: Data received: username = " + username + "\nhint = " + hint + "\nword = " + word)

    return "0"


@testing_routes.route('/pepperanimationPEPPER', methods=['POST'])
def receive_pepperanimation():
    try:
        content = request.json
        if content is None:
            print("MOCK PEPPER: Error! Empty JSON in pepperanimation")
            return "1"

        animation = content['animation']
    except KeyError:
        print("MOCK PEPPER: Error! Missing username,hint,or word!")
        return "1"

    print("MOCK PEPPER: Animation received = " + animation)

    return "0"


@testing_routes.route('/sendresultsPEPPER', methods=['POST'])
def receive_sendresults():
    try:
        content = request.json
        if content is None:
            print("MOCK PEPPER: Error! Empty JSON in sendresults")
            return "1"

        time = content['time_taken']
        lives = content['lives_left']
    except KeyError:
        print("MOCK PEPPER: Error! Missing username,hint,or word!")
        return "1"

    print("MOCK PEPPER: Data received: time = " + time + "\nlives = " + lives)

    return "0"


# Database tools:


# Wipes the Database
@testing_routes.route('/wipeDatabase', methods=['GET'])
def wipe_db():

    cloudsql.wipe()
    return 'DB Wiped'


# Show database, used HTML syntax for viewing in browser
@testing_routes.route('/showDB', methods=['GET'])
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