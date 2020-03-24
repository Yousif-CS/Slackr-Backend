'''
This module contains all the routes for message functionalities
'''
import message
from server import APP
from flask import request
from json import dumps

@APP.routes('/message/edit', methods=['PUT'])
def edit():
    '''
    Route to call message_edit
    '''
    payload = request.get_json()
    message.message_edit(payload["token"], payload["message_id"], payload["message"])
    return dumps({})
    