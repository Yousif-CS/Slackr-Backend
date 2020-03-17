import sys #pylint disable=missing-module-docstring
import pickle
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from error import InputError

#This dictionary will contain all of the database
#once the server starts and we unpickle the database file
#it is supposed to be {"Users": { "u_id": {"name_first": "Yousif", "name_last": "Khalid", "email": "whatever@gmail.com", "global_permission": 0, "channels": [channel_id1, channel_id2, ...]}},
#                      "Slack_owners: [u_id1, u_id2, ...], 
#                      "Channels":{"channel_id": {"name": "my_channel", "all_members":[u_id1, u_id2, ..], "owner_members" = [u_id1, u_id2], "messages"= [message_id1, message_id2]}},
#                      "Messages": {"message_id": {"message": "hello", "u_id": 12321, "time_created": 2323123232, "is_pinned" = True, "react_id": 1}}}
#Where each 
STORE = pickle.load("database.p", encoding="utf-8")

#this dictionary contains the session tokens that
#won't need to be stored in the Store data dictionary for pickling
TOKENS = {}

def get_store():
    '''
    Returns the global data structure STORE for modification by other functions
    in other files
    '''
    global STORE    #pylint: disable=global-statement
    return STORE

def get_tokens():
    '''
    Returns the global data structure Tokens for modification by other functions
    in other files
    '''
    global TOKENS   #pylint: disable=global-statement
    return TOKENS

def defaultHandler(err): #pylint: disable=missing-function-docstring
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

if __name__ == "__main__":
    APP.run(port=(int(sys.argv[1]) if len(sys.argv) == 2 else 8080))
