#pylint disable=missing-module-docstring
import sys 
import pickle
#modules used for asynchronously checking standups
import threading
import atexit
import message
import auth

from datetime import datetime
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from error import InputError
from standup import getStandup
#This dictionary will contain all of the database
#once the server starts and we unpickle the database file
#it is supposed to be {"Users": {u_id: {"name_first": "Yousif", "name_last": "Khalid", "email": "whatever@gmail.com", "handle": "ykhalid", "global_permission": 0, "channels": [channel_id1, channel_id2, ...]}},
#                      "Slack_owners": [u_id1, u_id2, ...],
#                      "Channels":{channel_id: {"name": "my_channel", "all_members":[u_id1, u_id2, ..], "owner_members" = [u_id1, u_id2], "is_private": False,  "messages"= [message_id1, message_id2]}},
#                      "Messages": [{"message_id": 123, "message": "hello", "u_id": 12321, "time_created": 2323123232, "is_pinned": True, "reacts": {"react_id": 1, "u_ids": [u_id1, u_id2,...], "is_this_user_reacted": True}}}]
#Where each 
STORE = pickle.load("database.p", encoding="utf-8")

#this dictionary contains the session tokens that
#won't need to be stored in the Store data dictionary for pickling
# {"token_str1": u_id1, "token_str2": u_id2, ..}
TOKENS = {}

#This data is related to managing standups generally
#a lock to control access to the standup's data dict
CHECKING_TIMER = 1  #check every second for the time
datalock = threading.Lock()
#thread handler
thread = threading.Thread()

def interrupt():
    global thread
    thread.cancel()

def manageStandups():
    '''
    checks every second if any standup is due and sends it
    '''
    global thread
    standup_info = getStandup()
    #if there are no standups, keep checking
    if standup_info == []:
        thread.start()
     
    with datalock:
        current_time = datetime.now()
        for standup in standup_info:
            if standup['finish_time'] == current_time:
                to_remove = standup_info.pop(standup)
                to_send = '\n'.join(to_remove['messages'])
                token = auth.get_token(TOKENS)
                if token == None:
                    #temporarily log the user in to send the message then log him out
                    token = auth.generate_token(to_remove['u_id'])
                    message.message_send(token, to_remove['channel_id'], to_send)
                    auth.auth_logout(to_remove['u_id'])
                else:
                    message.message_send(token, to_remove['channel_id'], to_send)

    thread = threading.Timer(CHECKING_TIMER, manageStandups, ())
    thread.start()

def StandupsInitialise():
    '''
    initialises the standups managing thread
    '''
    global thread
    thread = threading.Thread(CHECKING_TIMER, manageStandups, ())
    thread.start()

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
