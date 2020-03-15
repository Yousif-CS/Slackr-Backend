#Auth functions
import is_valid_email
import hashlib
from json import dumps
from flask import Flask, request
from error import InputError, AccessError
APP = Flask(__name__)


Store  = {
    'users': []

}
def retrieveStore():
    global Store
    return Store


def createtoken(email):
    pass

def create_uid(email):
    pass


def encrypt_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def create_handle(first_name, last_name):

    handle = first_name.lower() + last_name.lower()
    if len(handle) <= 20:
        return handle

    return 0


@APP.route('/auth/register', methods=['POST'])
def create():
    data = request.get_json()
    Store = retrieveStore()

    if is_valid_email(data['email'] == False):
        raise InputError(f'Email is invalid')

    if len(data['password']) < 6: 
        raise InputError(f'Password is too short')

    if len(data['name_first']) < 1 or len(data['name_first']) > 50:
        raise InputError(f'First name is not between 1 and 50 characters inclusively')

    if len(data['name_last']) < 1 or len(data['name_last']) > 50:
        raise InputError(f'Last name is not between 1 and 50 characters inclusively')

    for user in Store['users']:
        if user['email'] == data['email']:
            raise InputError(f'Email already taken')

    hashed_password = encrypt_password(data['password'])
    handle = create_handle(data['name_first'], data['name_last'])

    Store['users'].append({
        'email': data['email'],
        'password': hashed_password,
        'first_name': data['name_first'],
        'last_name': data['name_last'],
        'handle': handle

    })

    return dumps({
        'u_id' : create_uid(data['email']),
        'token': createtoken(data['email'])
    })

if __name__ == "__main__":
    print(create_handle('Max', 'Smith'))