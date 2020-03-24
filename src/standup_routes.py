'''
This module contains all the routes for standup functionalities
'''

import json
from flask import request

import standup
from server import APP

@APP.route('/standup/start', methods=['POST'])
def st_start():
    '''
    Wrapper for standup_start
    '''
    payload = request.get_json()
    to_send = standup.standup_start(payload['token'], \
        payload['channel_id'], payload['length'])
    return json.dumps(to_send)

@APP.route('/standup/active', methods=['GET'])
def st_active():
    '''
    Wrapper for standup_active
    '''
    payload = request.get_json()
    to_send = standup.standup_active(payload['token'], payload['channel_id'])
    return json.dumps(to_send)

@APP.route('/standup/send', methods=['POST'])
def st_send():
    '''
    Wrapper for standup_send
    '''
    payload = request.get_json()
    standup.standup_send(payload['token'], \
        payload['channel_id'], payload['message'])
    return json.dumps({})
