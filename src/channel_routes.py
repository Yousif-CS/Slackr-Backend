'''
This module contains all the routes for channel functionalities
'''

import json
from flask import Flask, request

import channel
from server import APP


@APP.route('/channel/invite', methods= ['POST'])
def invite(): 
    '''
    A route to call channel invites
    '''
    payload = request.get_json()
    channel.channel_invite(payload['token'], payload['channel_id'], payload['u_id'])
    return json.dumps({ })


@APP.route('/channel/details', methods= ['GET'])
def details(): 
    ''' 
    A route to gather a channel's details
    ''' 
    payload = request.get_json()
    info = channel.channel_details(payload['token'], payload['channel_id'])
    return json.dumps(info)

@APP.route('/channel/messages', methods=['GET'])
def messages():
    '''
    A route to call channel_messages
    '''
    payload = request.get_json()
    to_send = channel.channel_messages(payload['token'], \
        payload['channel_id'], payload['start'])
    return json.dumps(to_send)

@APP.route('/channel/leave', methods=['POST'])
def leave():
    '''
    A route to call channel_leave
    '''
    payload = request.get_json()
    channel.channel_leave(payload['token'], payload['channel_id'])
    return json.dumps({})

@APP.route('/channel/join', methods=['POST'])
def join():
    '''
    A route to call channel_join
    '''
    payload = request.get_json()
    channel.channel_join(payload['token'], payload['channel_id'])
    return json.dumps({})

@APP.route('/channel/addowner', methods=['POST'])
def addowner():
    '''
    A route to call channel_addowner
    '''
    payload = request.get_json()
    channel.channel_addowner(payload['token'], \
        payload['channel_id'], payload['u_id'])
    return json.dumps({})

@APP.route('/channel/removeowner', methods=['POST'])
def removeowner():
    '''
    A route to call channel_removeowner
    '''
    payload = request.get_json()
    channel.channel_removeowner(payload['token'], \
        payload['channel_id'], payload['u_id'])
    return json.dumps({})
    