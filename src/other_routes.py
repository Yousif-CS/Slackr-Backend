'''
This module contains all the routes for miscellaneous functionalities
'''

from flask import request, Blueprint
OTHER = Blueprint('other', __name__)

import json
import other
from error import RequestError


@OTHER.route('/admin/userpermission/change', methods=['POST'])
def u_per_change():
    '''
    A wrapper for userpermission_change
    '''
    payload = request.get_json()

    if not payload['token'] or not payload['u_id'] or not payload['permission_id']:
        raise RequestError(description=f"Missing data in request body")

    other.userpermission_change(payload['token'], payload['u_id'], payload['permission_id'])
    return json.dumps({})

@OTHER.route('/users/all', methods=['GET'])
def users_all():
    '''
    Wrapper for users_all
    '''
    payload = request.get_json()

    if not payload['token']:
        raise RequestError(description="Missing data in request body")
    
    every_user = other.users_all(payload['token'])
    return json.dumps(every_user)

@OTHER.route('/search', methods=['GET'])
def search():
    '''
    Wrapper for search
    '''
    payload = request.get_json()

    if not payload["token"] or (not payload["query_str"] and not payload["query_str"] == ""):
        raise RequestError(description="Missing data in request body")

    matching_msgs = other.search(payload["token"], payload["query_str"])
    return json.dumps(matching_msgs)

@OTHER.route('/workspace/reset', methods=['POST'])
def reset():
    other.workspace_reset()
    return json.dumps({})
    
