'''
This module contains all the routes for miscellaneous functionalities
'''

import json
from flask import request

import other
from server import APP
from error import RequestError

@APP.route('/admin/userpermission/change', methods=['POST'])
def u_per_change():
    '''
    A wrapper for userpermission_change
    '''
    payload = request.get_json()

    if not payload['token'] or not payload['u_id'] or not payload['permission_id']:
        raise RequestError(description=f"Missing data in request body")

    other.userpermission_change(payload['token'], \
        payload['u_id'], payload['permission_id'])
    return json.dumps({})