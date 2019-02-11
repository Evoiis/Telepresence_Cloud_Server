from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# -------------------MODELS------------------------


# Model for each registered robot
class Pepper(db.Model):
    pep_id = db.Column(db.String(100), primary_key=True)    # Identifier for Robot
    ip_address = db.Column(db.String(100))                  # Used to send requests to server on Robot
    PSK = db.Column(db.String(100))                         # Pepper Security Key for authentication between Robot software and server

    def __init__(self, pep_id, ip_address, PSK):
        self.pep_id = pep_id
        self.ip_address = ip_address
        self.PSK = PSK


#  User Authorization model that links a pep_id and a username.
class UserAuth(db.Model):
    pep_id = db.Column(db.String(100), primary_key=True)    # Identifier for Robot from Pepper Model
    username = db.Column(db.String(100), primary_key=True)  # Identifier for User from User Model
    email = db.Column(db.String(100))
    authorized = db.Column(db.Boolean)                      # True for when a user is authorized for a pep_id, False for when a user is requesting authorization

    def __init__(self, pep_id, username, email, authorized):
        self.pep_id = pep_id
        self.username = username
        self.email = email
        self.authorized = authorized


# Model for each registered user
class User(db.Model):
    username = db.Column(db.String(100), primary_key=True)
    email = db.Column(db.String(100))
    name = db.Column(db.String(100))
    password = db.Column(db.String(100))
    ASK = db.Column(db.String(100))                         # Android Security Key for authentication between Android app and server
    FBToken = db.Column(db.String(200))                     # Firebase Token for sending notifications and hangman game data

    def __init__(self, username, email, name, password, ASK, FBToken):
        self.username = username
        self.email = email
        self.name = name
        self.password = password
        self.ASK = ASK
        self.FBToken = FBToken

# ----------------DB-FUNCTIONS------------------------


# Adds a new record to the database
def create(model_name, content):
    if model_name == 'Pepper':
        model = Pepper(**content)
    elif model_name == 'Auth':
        model = UserAuth(**content)
    elif model_name == 'User':
        model = User(**content)
    else:
        return -1

    db.session.add(model)
    db.session.commit()
    return 0


# Gets a record of a model with its Primary Key matching content
def read(model_name, content):
    model = getModel(model_name)

    if model is None:
        return -1

    query = model.query.get(content)

    return query


# Gets a filtered list of all records of a model
def read_list(model_name, content):
    model = getModel(model_name)

    if model is None:
        return -1
    query = model.query.filter_by(**content).all()

    return query


# Gets all records of a model
def read_all(model_name):
    model = getModel(model_name)

    if model is None:
        return -1

    query = model.query.all()

    return query


# Updates record with data in content
def update(record, content):

    for key in content.keys():
        setattr(record, key, content[key])

    db.session.commit()

    return 0


# Deletes record from database
def delete(record):

    db.session.delete(record)
    db.session.commit()

    return 0


def wipe():
    db.drop_all()
    db.create_all()
    return 0


def initialize_db(app):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    print("Database initialized.")

# ---------------HELPER-FUNCTIONS------------------------


def getModel(model_name):
    if model_name == 'Pepper':
        model = Pepper
    elif model_name == 'Auth':
        model = UserAuth
    elif model_name == 'User':
        model = User
    else:
        return None

    return model
