'''
This module contains all the routes for miscellaneous functionalities
'''

import json
from flask import request, Blueprint
import other
from error import RequestError

OTHER = Blueprint('other', __name__)


@OTHER.route('/admin/userpermission/change', methods=['POST'])
def u_per_change():
    '''
    A wrapper for userpermission_change
    '''
    payload = request.get_json()

    if not payload['token'] or not payload['u_id'] or not payload['permission_id']:
        raise RequestError(description=f"Missing data in request body")

    other.userpermission_change(
        payload['token'], int(payload['u_id']), int(payload['permission_id']))
    return json.dumps({})


@OTHER.route('/users/all', methods=['GET'])
def users_all():
    '''
    Wrapper for users_all
    '''
    token = request.args.get('token')

    if not token:
        raise RequestError(description="Missing data in request body")

    every_user = other.users_all(token)
    return json.dumps(every_user)


@OTHER.route('/search', methods=['GET'])
def search():
    '''
    Wrappers for search
    '''
    token = request.args.get('token')
    query_str = request.args.get('query_str')

    if not token or (not query_str and not query_str == ""):
        raise RequestError(description="Missing data in request body")

    matching_msgs = other.search(token, query_str)
    return json.dumps(matching_msgs)


@OTHER.route('/workspace/reset', methods=['POST'])
def reset():
    '''
    A route to reset the whole server database
    '''
    other.workspace_reset()
    return json.dumps({})
