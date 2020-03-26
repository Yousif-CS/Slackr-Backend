'''
This module contains all the routes for user functionalities
'''

import json
import user
from server import APP
from flask import request
from error import RequestError

@APP.route('/user/profile', methods=['GET'])
def profile():
    '''
    A route to call user_profile
    '''
    payload = request.get_json()

    if not payload["token"] or not payload["u_id"]:
        raise RequestError(description="Missing data in request body")

    to_send = user.user_profile(payload["token"], payload["u_id"])
    return json.dumps(to_send)

@APP.route('/user/profile/setname', methods=['PUT'])
def profile_setname():
    '''
    A route to call user_profile_setname
    '''
    payload = request.get_json()

    if not payload["token"] or not payload["name_first"] or not payload["name_last"]:
        raise RequestError(description="Missing data in request body")

    user.user_profile_setname(payload["token"], payload["name_first"], payload["name_last"])
    return json.dumps({})

@APP.route('/user/profile/setemail', methods=['PUT'])
def profile_setemail():
    '''
    A route to call user_profile_setemail
    '''
    payload = request.getjson()

    if not payload["token"] or not payload["email"]:
        raise RequestError(description="Missing data in request body")

    user.user_profile_setemail(payload["token"], payload["email"])
    return json.dumps({})

@APP.route('/user/profile/sethandle', methods=['PUT'])
def profile_sethandle():
    '''
    A route to call user_profile_sethandle
    '''
    payload = request.getjson()

    if not payload["token"] or not payload["handle_str"]:
        raise RequestError(description="Missing data in request body")

    user.user_profile_sethandle(payload["token"], payload["handle_str"])
    return json.dumps({})
    