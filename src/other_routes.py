'''
This module contains all the routes for miscellaneous functionalities
'''

import json
import other
from server import APP
from flask import request

@APP.route('/users/all', methods=['GET'])
def users_all():
    '''
    Route to call users_all
    '''
    payload = request.get_json()
    to_send = other.users_all(payload["token"])
    return json.dumps(to_send)

@APP.route('/search', methods=['GET'])
def search():
    '''
    Route to call search
    '''
    payload = request.get_json()
    to_send = other.search(payload["token"], payload["query_str"])
    return json.dumps(to_send)
    