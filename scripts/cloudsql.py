
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


#  Model acting as a junction table between Peppers and Users
class UserAuth(db.Model):
    pep_id = db.Column(db.String(100), primary_key=True)
    username = db.Column(db.String(100), primary_key=True)
    email = db.Column(db.String(100))
    authorized = db.Column(db.Boolean)

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
    ASK = db.Column(db.String(100))         # Android Security Key for authentication between Android app and server
    FBToken = db.Column(db.String(200))     # Firebase Token for sending notifications and hangman game data

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
        record.key = content[key]

    db.session.commit()

    return 0


# Deletes record from database
def delete(record):

    db.session.delete(record)
    db.session.commit()

    return 0


def wipe_db():
    db.drop_all()
    db.create_all()
    return "Database wiped."


def ini_db(app):
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


# -----------TEST-SET--------------------------------
def test_set():
    admin = User(username='admin', email='admin@example.com', name='Atho', password='admin', ASK='asdf', FBToken='')
    subin = User(username='subin', email='subin@example.com', name='S', password='subin', ASK='asdf', FBToken='')
    david = User(username='david', email='david@example.com', name='D', password='david', ASK='asdf', FBToken='')
    kass = User(username='kass', email='kass@example.com', name='K', password='kass', ASK='asdf', FBToken='')

    adminSalt = UserAuth(pep_id='salt', username='admin', email='admin@example.com', authorized=True)
    subinSalt = UserAuth(pep_id='salt', username='subin', email='subin@example.com', authorized=True)
    davidSalt = UserAuth(pep_id='salt', username='david', email='david@example.com', authorized=True)
    kassSalt = UserAuth(pep_id='salt', username='kass', email='kass@example.com', authorized=True)

    adminFraser = UserAuth(pep_id='fraser', username='admin', email='admin@example.com', authorized=False)
    subinFraser = UserAuth(pep_id='fraser', username='subin', email='subin@example.com', authorized=False)
    davidFraser = UserAuth(pep_id='fraser', username='david', email='david@example.com', authorized=False)
    kassFraser = UserAuth(pep_id='fraser', username='kass', email='kass@example.com', authorized=False)

    salt = Pepper(pep_id='Salt', ip_address='10.0.0.3', PSK='asdf')
    fraser = Pepper(pep_id='fraser', ip_address='10.0.0.4', PSK='asdf')
    simon = Pepper(pep_id='simon', ip_address='10.0.0.5', PSK='asdf')
    fan = Pepper(pep_id='fan', ip_address='10.0.0.6', PSK='asdf')
    window = Pepper(pep_id='window', ip_address='10.0.0.7', PSK='asdf')

    db.session.add_all([admin, subin, david, kass])
    db.session.add_all([adminSalt, adminFraser, subinSalt, davidSalt, subinFraser, davidFraser, kassFraser, kassSalt])
    db.session.add_all([salt, fraser, simon, fan, window])
    db.session.commit()