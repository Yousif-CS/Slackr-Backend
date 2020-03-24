'''
This module contains all the routes for standup functionalities
'''

import json
import standup
from server import APP
from flask import request

@APP.routes('/standup/start', methods=['POST'])
def standup_start():
    '''
    Route to call standup_start
    '''
    payload = request.get_json()
    to_send = standup.standup_start(payload["token"], payload["channel_id"], payload("length"))
    return json.dumps(to_send)
    