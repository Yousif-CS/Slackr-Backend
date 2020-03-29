'''
This module contains all the routes for channel functionalities
'''

from flask import request, Blueprint
CHANNEL = Blueprint('channel', __name__)
import json

import channel
from error import RequestError


@CHANNEL.route('/invite', methods=['POST'])
def invite(): 
    '''
    A route to call channel invites
    '''
    payload = request.get_json()
    if not payload['token'] or not payload['channel_id'] or not payload['u_id']: 
        raise RequestError(description="Missing data in request body")

    channel.channel_invite(payload['token'], payload['channel_id'], payload['u_id'])
    return json.dumps({})


@CHANNEL.route('/details', methods=['GET'])
def details(): 
    ''' 
    A route to gather a channel's details
    ''' 
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    if not token or not channel_id: 
        raise RequestError(description="Missing data in request body")

    info = channel.channel_details(token, int(channel_id))
    return json.dumps(info)

@CHANNEL.route('/messages', methods=['GET'])
def messages():
    '''
    A route to call channel_messages
    '''
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    start = request.args.get('start')

    if not token or not channel_id or start is None:
        raise RequestError(description="Missing data in request body")

    to_send = channel.channel_messages(token, \
        int(channel_id), int(start))

    return json.dumps(to_send)

@CHANNEL.route('/leave', methods=['POST'])
def leave():
    '''
    A route to call channel_leave
    '''
    payload = request.get_json()

    if not payload['token'] or not payload['channel_id']:
        raise RequestError(description="Missing data in request body")

    channel.channel_leave(payload['token'], payload['channel_id'])
    return json.dumps({})

@CHANNEL.route('/join', methods=['POST'])
def join():
    '''
    A route to call channel_join
    '''
    payload = request.get_json()

    if not payload['token'] or not payload['channel_id']:
        raise RequestError(description="Missing data in request body")

    channel.channel_join(payload['token'], payload['channel_id'])
    return json.dumps({})

@CHANNEL.route('/addowner', methods=['POST'])
def addowner():
    '''
    A route to call channel_addowner
    '''
    payload = request.get_json()

    if not payload['token'] or not payload['channel_id'] or not payload['u_id']:
        raise RequestError(description="Missing data in request body")

    channel.channel_addowner(payload['token'], \
        payload['channel_id'], payload['u_id'])

    return json.dumps({})

@CHANNEL.route('/removeowner', methods=['POST'])
def removeowner():
    '''
    A route to call channel_removeowner
    '''
    payload = request.get_json()

    if not payload['token'] or not payload['channel_id'] or not payload['u_id']:
        raise RequestError(description="Missing data in request body")

    channel.channel_removeowner(payload['token'], \
        payload['channel_id'], payload['u_id'])

    return json.dumps({})
