'''
This module contains all the routes for channel functionalities
'''

import json
from flask import request

import channel
from server import APP
from error import RequestError

@APP.route('/channel/messages', methods=['GET'])
def messages():
    '''
    A route to call channel_messages
    '''
    payload = request.get_json()

    if not payload['token'] or not payload['channel_id'] or not payload['start']:
        raise RequestError(description=f"Missing data in request body")

    to_send = channel.channel_messages(payload['token'], \
        payload['channel_id'], payload['start'])

    return json.dumps(to_send)

@APP.route('/channel/leave', methods=['POST'])
def leave():
    '''
    A route to call channel_leave
    '''
    payload = request.get_json()

    if not payload['token'] or not payload['channel_id']:
        raise RequestError(description=f"Missing data in request body")

    channel.channel_leave(payload['token'], payload['channel_id'])
    return json.dumps({})

@APP.route('/channel/join', methods=['POST'])
def join():
    '''
    A route to call channel_join
    '''
    payload = request.get_json()

    if not payload['token'] or not payload['channel_id']:
        raise RequestError(description=f"Missing data in request body")

    channel.channel_join(payload['token'], payload['channel_id'])
    return json.dumps({})

@APP.route('/channel/addowner', methods=['POST'])
def addowner():
    '''
    A route to call channel_addowner
    '''
    payload = request.get_json()

    if not payload['token'] or not payload['channel_id'] or not payload['u_id']:
        raise RequestError(description=f"Missing data in request body")

    channel.channel_addowner(payload['token'], \
        payload['channel_id'], payload['u_id'])

    return json.dumps({})

@APP.route('/channel/removeowner', methods=['POST'])
def removeowner():
    '''
    A route to call channel_removeowner
    '''
    payload = request.get_json()

    if not payload['token'] or not payload['channel_id'] or not payload['u_id']:
        raise RequestError(description=f"Missing data in request body")

    channel.channel_removeowner(payload['token'], \
        payload['channel_id'], payload['u_id'])

    return json.dumps({})
