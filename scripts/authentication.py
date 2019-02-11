import cloudsql
import hashlib
import random
import string

# --------------AUTHENTICATION-FUNCTIONS------------------------


def check_PSK(key, pep_id):
    pepper_query = cloudsql.read('Pepper', pep_id)
    if pepper_query is None:
        return None

    current_cloud_key = pepper_query.PSK
    next_cloud_key = hash_PSK(current_cloud_key)

    if next_cloud_key == key:

        updates = {'PSK': next_cloud_key}
        cloudsql.update(pepper_query, updates)

        return True
    else:
        return False


def hash_PSK(key):
    salt = '<Salt String>'
    key += salt
    result = hashlib.sha256(key).hexdigest()
    return result


def check_ASK(key, username):
    user_query = cloudsql.read('User', username)
    if user_query is None:
        return None

    current_cloud_key = user_query.ASK
    next_cloud_key = hash_ASK(current_cloud_key)

    if next_cloud_key == key:

        updates = {'ASK': next_cloud_key}
        cloudsql.update(user_query, updates)
        return True
    else:
        return False


def hash_ASK(key):
    salt = '<Salt String>'
    key += salt
    key.encode('utf-8')
    result = hashlib.md5(key).hexdigest()
    return result


def generate_random_string():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(15))