from scripts import game_routes, pepper_routes, android_routes, user_routes
from scripts import cloudsql
from flask import Flask
import firebase_admin
import config

TESTING_MODE = False

app = Flask(__name__)
app.register_blueprint(game_routes.game)
app.register_blueprint(pepper_routes.pepper_routes)
app.register_blueprint(android_routes.android_routes)
app.register_blueprint(user_routes.user_routes)

if TESTING_MODE:
    from tests import testing_routes
    app.register_blueprint(testing_routes.testing_routes)

app.config.from_object(config)

# Local Instance:
cred = firebase_admin.credentials.Certificate('<Path to JSON credentials file>')
default_app = firebase_admin.initialize_app(cred)

# GCloud Instance:
# default_app = firebase_admin.initialize_app()


@app.errorhandler(500)
def server_error():
    return "An internal server error occurred.", 500


if __name__ == '__main__':
    cloudsql.initialize_db(app)
    app.run(host='0.0.0.0', port=8080)
