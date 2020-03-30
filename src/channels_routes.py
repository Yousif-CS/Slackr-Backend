'''
This module contains all the routes for channels functionalities
'''

from json import dumps
from flask import request, Blueprint
from channels import channels_list, channels_listall, channels_create
from error import RequestError

CHANNELS = Blueprint('channels', __name__)


@CHANNELS.route("/list", methods=['GET'])
def c_list():
    '''
    a route which calls channels_list
    '''
    token = request.args.get('token')

    if not token:
        raise RequestError(description="Missing data in request body")

    response = channels_list(token)
    return dumps(response)


@CHANNELS.route("/listall", methods=['GET'])
def listall():
    '''
    a route which calls channels_listall
    '''
    token = request.args.get('token')

    if not token:
        raise RequestError(description="Missing data in request body")

    response = channels_listall(token)
    return dumps(response)


@CHANNELS.route("/create", methods=['POST'])
def create():
    '''
    a route which calls channels_create
    '''
    data = request.get_json()

    if not data['token'] or not data['name'] or data['is_public'] is None:
        raise RequestError(description="Missing data in request body")

    response = channels_create(data['token'], data['name'], data['is_public'])
    return dumps(response)
