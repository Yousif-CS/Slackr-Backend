'''
This module contains all the routes for message functionalities
'''
from json import dumps
from flask import request

import message
from server import APP
from error import RequestError

@APP.route("/message/send", methods=['POST'])
def send():
    '''
    calls message_send from message
    '''
    data = request.get_json()

    if not data['token'] or not data['channel_id'] or not data['message']:
        raise RequestError(description="Missing data in request body")

    response = message.message_send(data['token'], data['channel_id'], data['message'])
    return dumps(response)

@APP.route("/message/sendlater", methods=['POST'])
def sendlater():
    '''
    calls message_send from message
    '''
    data = request.get_json()

    if not data['token'] or not data['channel_id'] or not data['message'] or not data['time_sent']:
        raise RequestError(description="Missing data in request body")

    response = message.message_sendlater(data['token'], data['channel_id'],\
        data['message'], data['time_sent'])
    return dumps(response)

@APP.route("/message/react", methods=['POST'])
def react():
    '''
    a route that calls message_react from message
    '''
    data = request.get_json()

    if not data['token'] or not data['message_id'] or not data['react_id']:
        raise RequestError(description="Missing data in request body")

    message.message_react(data['token'], data['message_id'], data['react_id'])
    return dumps({})

@APP.route("/message/unreact", methods=['POST'])
def unreact():
    '''
    a route that calls message_unreact from message
    '''
    data = request.get_json()

    if not data['token'] or not data['message_id'] or not data['react_id']:
        raise RequestError(description="Missing data in request body")

    message.message_unreact(data['token'], data['message_id'], data['react_id'])
    return dumps({})

@APP.route("/message/pin", methods=['POST'])
def pin():
    '''
    a route which calls message_pin from message
    '''
    data = request.get_json()

    if not data['token'] or not data['message_id']:
        raise RequestError(description="Missing data in request body")

    message.message_pin(data['token'], data['message_id'])
    return dumps({})

@APP.route("/message/unpin", methods=['POST'])
def unpin():
    '''
    a route which calls message_pin from message
    '''
    data = request.get_json()

    if not data['token'] or not data['message_id']:
        raise RequestError(description="Missing data in request body")

    message.message_unpin(data['token'], data['message_id'])
    return dumps({})

@APP.route("/message/remove", methods=['DELETE'])
def delete():
    '''
    a route which calls message_delete from message
    '''
    data = request.get_json()

    if not data['token'] or not data['message_id']:
        raise RequestError(description="Missing data in request body")

    message.message_remove(data['token'], data['message_id'])
    return dumps({})

@APP.route("/message/edit", methods=['PUT'])
def edit():
    '''
    a route which calls message_edit from message
    '''
    data = request.get_json()

    if not data["token"] or not data["message_id"] or not data["message"]:
        raise RequestError(description="Missing data in request body")

    message.message_edit(data["token"], data["message_id"], data["message"])
    return dumps({})
