'''
State variables and functions to deal
with the server's data when its launched
'''
from threading import Timer, Thread
import pickle
import time

# This dictionary will contain all of the database
# once the server starts and we unpickle the database file
# it is supposed to be {
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
STORE = dict()

# this dictionary contains the session tokens that
# won't need to be stored in the Store data dictionary for pickling
# {"token_str1": u_id1, "token_str2": u_id2, ..}
TOKENS = dict()


def get_store():
    '''
    Returns the global data structure STORE for modification by other functions
    in other files
    '''
    global STORE  # pylint: disable=global-statement
    return STORE


def get_tokens():
    '''
    Returns the global data structure Tokens for modification by other functions
    in other files
    '''
    global TOKENS  # pylint: disable=global-statement
    return TOKENS


def initialize_store():
    '''
    Initialize the server database dictionary, creates an empty dictionary if the
    database file is empty
    '''
    global STORE  # pylint: disable=global-statement
    with open('database.p', "rb") as file:
        try:
            STORE = pickle.load(file, encoding="utf-8")
        except EOFError:
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
    global TOKENS  # pylint: disable=global-statement
    TOKENS = dict()


# A constant to update the database every hour
SECONDS_TO_UPDATE = 1


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
    global STORE
    with open('database.p', "wb") as database_file:
        pickle.dump(STORE, database_file)

# a Timer to update the database every hour
DATABASE_UPDATER = StateTimer(SECONDS_TO_UPDATE, update_database)

def run_updater():
    '''
    a function that initializes the database updater in parallel
    '''
    DATABASE_UPDATER.run()
# the thread that parallelizes the work
UPDATE_THREAD = Thread(target=run_updater)

# initialize state when imported
initialize_state()
