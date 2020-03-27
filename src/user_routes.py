'''
This module contains all the routes for user functionalities
'''

import json
import user
from flask import request, Blueprint

USER = Blueprint('user', __name__)

@USER.route('/profile', methods=['GET'])
def profile():
    '''
    A route to call user_profile
    '''
    payload = request.get_json()
    to_send = user.user_profile(payload["token"], payload["u_id"])
    return json.dumps(to_send)

@USER.route('/profile/setname', methods=['PUT'])
def profile_setname():
    '''
    A route to call user_profile_setname
    '''
    payload = request.get_json()
    user.user_profile_setname(payload["token"], payload["name_first"], payload["name_last"])
    return json.dumps({})

@USER.route('/profile/setemail', methods=['PUT'])
def profile_setemail():
    '''
    A route to call user_profile_setemail
    '''
    payload = request.getjson()
    user.user_profile_setemail(payload["token"], payload["email"])
    return json.dumps({})

@USER.route('/profile/sethandle', methods=['PUT'])
def profile_sethandle():
    '''
    A route to call user_profile_sethandle
    '''
    payload = request.getjson()
    user.user_profile_sethandle(payload["token"], payload["handle_str"])
    return json.dumps({})