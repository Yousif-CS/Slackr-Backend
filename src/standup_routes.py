'''
This module contains all the routes for standup functionalities
'''

import json
from flask import request, Blueprint

import standup
from error import RequestError

STANDUP = Blueprint('standup', __name__)


@STANDUP.route('/start', methods=['POST'])
def st_start():
    '''
    Wrapper for standup_start
    '''
    payload = request.get_json()

    if not payload['token'] or not payload['channel_id'] or not payload['length']:
        raise RequestError(description=f"Missing data in request body")

    to_send = standup.standup_start(payload['token'],
                                    payload['channel_id'], payload['length'])

    return json.dumps(to_send)


@STANDUP.route('/active', methods=['GET'])
def st_active():
    '''
    Wrapper for standup_active
    '''
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')

    if not token or not channel_id:
        raise RequestError(description=f"Missing data in request body")

    to_send = standup.standup_active(token, int(channel_id))

    return json.dumps(to_send)


@STANDUP.route('/send', methods=['POST'])
def st_send():
    '''
    Wrapper for standup_send
    '''
    payload = request.get_json()

    if not payload['token'] or not payload['channel_id'] or not payload['message']:
        raise RequestError(description=f"Missing data in request body")

    standup.standup_send(payload['token'],
                         payload['channel_id'], payload['message'])

    return json.dumps({})
