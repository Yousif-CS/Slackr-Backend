'''
This module contains all the routes for channels functionalities
'''

from json import dumps
from flask import request
from channels import channels_list, channels_listall, channels_create
from server import APP

@APP.route("/channels/list", methods=['GET'])
def c_list():
    '''
    a route which calls channels_list
    '''
    data = request.get_json()
    response = channels_list(data['token'])
    return dumps(response)

@APP.route("/channels/listall", methods=['GET'])
def listall():
    '''
    a route which calls channels_listall
    '''
    data = request.get_json()
    response = channels_listall(data['token'])
    return dumps(response)



