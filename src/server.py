'''
The server that handles the routes for slackr
'''

import sys
import pickle
from flask import Flask, request

#This dictionary will contain all of the database
#once the server starts and we unpickle the database file
#it is supposed to be {
#                       "Users": {
#                                   u_id: {
#                                           "name_first": "Yousif",
#                                           "name_last": "Khalid",
#                                           "email": "whatever@gmail.com",
#                                           "password": "hashed_pw_str",
#                                           "handle": "ykhalid",
#                                           "global_permission": 0,
#                                           "channels": [channel_id1, channel_id2, ...]
#                                           }
#                                },
#                      "Slack_owners": [u_id1, u_id2, ...],
#                      "Channels": {
#                                   channel_id: {
#                                                   "name": "my_channel",
#                                                   "all_members":[u_id1, u_id2, ..],
#                                                   "owner_members" = [u_id1, u_id2],
#                                                   "is_private": False,
#                                                   "messages"= [message_id1, message_id2]
#                                               }
#                                  },
#                      "Messages": [{
#                                       "message_id": 123,
#                                       "message": "hello",
#                                       "u_id": 12321,
#                                       "time_created": 2323123232,
#                                       "is_pinned": True,
#                                       "reacts": [{
#                                                       "react_id": 1,
#                                                       "u_ids": [u_id1, u_id2,...],
#                                                       "is_this_user_reacted": True
#                                                  }, ...]
#                                   }]
#                   }

STORE = list()

#this dictionary contains the session tokens that
#won't need to be stored in the Store data dictionary for pickling
# {"token_str1": u_id1, "token_str2": u_id2, ..}
TOKENS = dict()

APP = Flask(__name__)


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

from threading import Timer
from json import dumps
from flask_cors import CORS

#these are routes imports
import channel_routes
import channels_routes
import user_routes
import auth_routes
import standup_routes
import message_routes

from error import InputError
       
#A constant to update the database every hour
SECONDS_TO_UPDATE = 3600

class StateTimer(Timer):
    '''
    An simple abstraction over the timer class to
    run a function every n seconds
    '''
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

def update_database():
    '''
    pickle the state database into a file
    '''
    with open('database.p', "wb") as database_file:
        pickle.dump(STORE, database_file)

#a Timer to update the database every hour
DATABASE_UPDATER = StateTimer(SECONDS_TO_UPDATE, update_database)

def initialize_store():
    '''
    Initialize the server database dictionary, creates an empty dictionary if the
    database file is empty
    '''
    global STORE    #pylint: disable=global-statement
    with open('database.p', "rb") as file:
        STORE = pickle.load(file, encoding="utf-8")
        if STORE is None:
            STORE = {
                'Users': {},
                'Slack_owners': [],
                'Channels': {},
                'Messages': [],
            }

def initialize_state():
    '''
    initialise the store and the tokens dictionary
    '''
    initialize_store()
    global TOKENS   #pylint: disable=global-statement
    TOKENS = dict()


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
    initialize_state()
    DATABASE_UPDATER.start()
    APP.run(port=(int(sys.argv[1]) if len(sys.argv) == 2 else 8080))
