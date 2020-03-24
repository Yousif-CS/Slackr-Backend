'''
This module contains all the routes for message functionalities
'''
from json import dumps
from flask import request
import message
from server import APP

@APP.route("/message/send", methods=['POST'])
def send():
    '''
    calls message_send from message
    '''
    data = request.get_json()
    response = message.message_send(data['token'], data['channel_id'], data['message'])
    return dumps(response)

@APP.route("/message/sendlater", methods=['POST'])
def sendlater():
    '''
    calls message_send from message
    '''
    data = request.get_json()
    response = message.message_sendlater(data['token'], data['channel_id'],\
        data['message'], data['time_sent'])
    return dumps(response)