'''
This module contains all the routes for auth functionalities
'''
from json import dumps
from flask import request, Blueprint
from auth import auth_register, auth_login, auth_logout, auth_passwordreset_request, auth_passwordreset_reset
from error import RequestError
AUTH = Blueprint('auth', __name__)


@AUTH.route('/register', methods=['POST'])
def create_user():
    '''
    A route to register a user
    '''
    payload = request.get_json()
    if not payload['email'] or not payload['password'] \
            or not payload['name_first'] or not payload['name_last']:
        raise RequestError(description="Missing data in request body")

    reg_info = auth_register(
        payload['email'], payload['password'], payload['name_first'], payload['name_last'])
    return dumps(reg_info)


@AUTH.route('/login', methods=['POST'])
def connect():
    '''
    A route to login a user
    '''
    payload = request.get_json()
    if not payload['email'] or not payload['password']:
        raise RequestError(description="Missing data in request body")

    login_info = auth_login(payload['email'], payload['password'])
    return dumps(login_info)


@AUTH.route('/logout', methods=['POST'])
def disconnect():
    '''
    A route to logout the user
    '''
    payload = request.get_json()
    if not payload['token']:
        raise RequestError(description="Missing data in request body")
    successful = auth_logout(payload['token'])
    return dumps(successful)


@AUTH.route('/passwordreset/request', methods=['POST'])
def send_email():
    '''
    A route to send a reset code via email to a user
    '''
    payload = request.get_json()
    if not payload['email']:
        raise RequestError(description="Missing data in request body")
    auth_passwordreset_request(payload['email'])
    return dumps({})


@AUTH.route('/passwordreset/reset', methods=['POST'])
def reset_password():
    '''
    A route to reset a user's password
    '''
    payload = request.get_json()
    if not payload['reset_code'] or not payload['new_password']:
        raise RequestError(description="Missing data in request body")

    auth_passwordreset_reset(payload['reset_code'], payload['new_password'])
    return dumps({})
