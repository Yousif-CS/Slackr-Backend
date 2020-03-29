'''
This module contains all the routes for user functionalities
'''

import json
from flask import request, Blueprint
import user
from error import RequestError

USER = Blueprint('user', __name__)

@USER.route('/profile', methods=['GET'])
def profile():
    '''
    A route to call user_profile
    '''
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    if not token or not u_id:
        raise RequestError(description="Missing data in request body")

    to_send = user.user_profile(token, u_id)
    return json.dumps(to_send)

@USER.route('/profile/setname', methods=['PUT'])
def profile_setname():
    '''
    A route to call user_profile_setname
    '''
    payload = request.get_json()

    if not payload["token"] or not payload["name_first"] or not payload["name_last"]:
        raise RequestError(description="Missing data in request body")

    user.user_profile_setname(payload["token"], payload["name_first"], payload["name_last"])
    return json.dumps({})

@USER.route('/profile/setemail', methods=['PUT'])
def profile_setemail():
    '''
    A route to call user_profile_setemail
    '''
    payload = request.get_json()

    if not payload["token"] or not payload["email"]:
        raise RequestError(description="Missing data in request body")

    user.user_profile_setemail(payload["token"], payload["email"])
    return json.dumps({})

@USER.route('/profile/sethandle', methods=['PUT'])
def profile_sethandle():
    '''
    A route to call user_profile_sethandle
    '''
    payload = request.get_json()

    if not payload["token"] or not payload["handle_str"]:
        raise RequestError(description="Missing data in request body")

    user.user_profile_sethandle(payload["token"], payload["handle_str"])
    return json.dumps({})
    