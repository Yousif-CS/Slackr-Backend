'''
This module contains all the routes for message functionalities
'''
from json import dumps
from flask import request, Blueprint

import message
from error import RequestError

MESSAGE = Blueprint('messages', __name__)
@MESSAGE.route("/send", methods=['POST'])
def send():
    '''
    calls message_send from message
    '''
    data = request.get_json()

    if not data['token'] or not data['channel_id'] or not data['message']:
        raise RequestError(description="Missing data in request body")

    response = message.message_send(
        data['token'], int(data['channel_id']), data['message'])
    return dumps(response)


@MESSAGE.route("/sendlater", methods=['POST'])
def sendlater():
    '''
    calls message_send from message
    '''
    data = request.get_json()

    if not data['token'] or not data['channel_id'] or not data['message'] or not data['time_sent']:
        raise RequestError(description="Missing data in request body")

    response = message.message_sendlater(data['token'], int(data['channel_id']),
                                         data['message'], int(data['time_sent']))
    return dumps(response)


@MESSAGE.route("/react", methods=['POST'])
def react():
    '''
    a route that calls message_react from message
    '''
    data = request.get_json()

    if not data['token'] or not data['message_id'] or not data['react_id']:
        raise RequestError(description="Missing data in request body")

    message.message_react(data['token'], int(data['message_id']), int(data['react_id']))
    return dumps({})


@MESSAGE.route("/unreact", methods=['POST'])
def unreact():
    '''
    a route that calls message_unreact from message
    '''
    data = request.get_json()

    if not data['token'] or not data['message_id'] or not data['react_id']:
        raise RequestError(description="Missing data in request body")

    message.message_unreact(
        data['token'], int(data['message_id']), int(data['react_id']))
    return dumps({})


@MESSAGE.route("/pin", methods=['POST'])
def pin():
    '''
    a route which calls message_pin from message
    '''
    data = request.get_json()

    if not data['token'] or not data['message_id']:
        raise RequestError(description="Missing data in request body")

    message.message_pin(data['token'], int(data['message_id']))
    return dumps({})


@MESSAGE.route("/unpin", methods=['POST'])
def unpin():
    '''
    a route which calls message_pin from message
    '''
    data = request.get_json()

    if not data['token'] or not data['message_id']:
        raise RequestError(description="Missing data in request body")

    message.message_unpin(data['token'], int(data['message_id']))
    return dumps({})


@MESSAGE.route("/remove", methods=['DELETE'])
def delete():
    '''
    a route which calls message_delete from message
    '''
    data = request.get_json()

    if not data['token'] or not data['message_id']:
        raise RequestError(description="Missing data in request body")

    message.message_remove(data['token'], int(data['message_id']))
    return dumps({})


@MESSAGE.route("/edit", methods=['PUT'])
def edit():
    '''
    a route which calls message_edit from message
    '''
    data = request.get_json()

    if not data["token"] or not data["message_id"] \
        or (not data["message"] and not data["message"] == ""):
        raise RequestError(description="Missing data in request body")

    message.message_edit(data["token"], int(data["message_id"]), data["message"])
    return dumps({})
