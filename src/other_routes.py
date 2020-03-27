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

    other.userpermission_change(payload['token'], \
        payload['u_id'], payload['permission_id'])
    return json.dumps({})

@OTHER.route('/workspace/reset', methods=['POST'])
def reset():
    '''
    A wrapper for reseting the workspace
    '''
    other.workspace_reset()
    return json.dumps({})
