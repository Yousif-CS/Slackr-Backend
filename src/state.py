'''
State variables and functions to deal
with the server's data when its launched
'''
from threading import Timer, Thread
import pickle
import time

from error import InputError, AccessError

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
# STORE = dict()


class Users():
    def __init__(self):
        self._users = dict()
        self._permissions = [1, 2]
        self._num_users = 0
    def add_user(self, email, password, f_name, l_name):
        '''
        adds user with given details to the database
        Arguments: first and last names, email, password, handle and permissions
        Returns: None
        Raises: InputError, AccessError
        '''
        if self.email_used(email):
            raise InputError("Email already used")

        if self._num_users == 0:
            

    def user_details(self, u_id):
        pass

    def all_users(self):
        pass

    def user_exists(self, u_id):
        pass
    def email_used(self, email):
        pass

class Admins(Users):
    def __init__(self):
        pass
    def add_admin(self, u_id):
        pass

    def is_admin(self, u_id):
        pass

class Channels():
    def __init__(self):
        self._channels = dict()
    def add(self, details):
        pass
    
    def join(self, channel_id, u_id):
        pass
    
    def leave(self, channel_id, u_id):
        pass
    
    def channel_exists(self, channel_id):
        pass

    def all(self):
        pass

    def is_member(self, channel_id, u_id):
        pass

    def is_owner(self, channel_id, u_id):
        pass

    def owners(self, channel_id):
        pass

    def members(self, channel_id):
        pass

class Messages():
    def __init__(self):
        self._messages = list()
        self._react_ids = [1]
        
    def add(self, details):
        pass

    def remove(self, message_id):
        pass

    def find(self, message_id):
        pass

    def search(self, query_string):
        pass

    def is_valid_react(self, react_id):
        pass

    def is_sender(self, message_id, u_id):
        pass

class User_Message():
    '''
    Contains a structure that maintains the relationship
    between users, channels and messages they sent
    '''
    def __init__(self):
        self._user_messages = list()

    def add_link(self, user_id, channel_id, message_id):
        pass

    def remove_link_by_user(self, user_id):
        pass

    def remove_link_by_channel(self, channel_id):
        pass
    
    def remove_link_by_message(self, channel_id):
        pass

class User_Channel():
    '''
    Contains a structure that maintains the relationship
    between users and the channels they have joined
    '''
    def __init__(self):
        self._user_channels = list()

    def add_link(self, user_id, channel_id):
        pass

    def remove_link_by_user(self, user_id):
        pass

    def remove_link_by_channel(self, channel_id):
        pass

class Database():
    def __init__(self):
        self.Users = Users()
        self.Admins = Admins()
        self.Channels = Channels()
        self.Messages = Messages()
        self.User_Message = User_Message()
        self.User_Channel = User_Channel()

    def add_admin(self, u_id):
        pass
    def remove_admin(self, u_id):
        pass
    def add_channel(self, u_id, channel_id, is_public):
        pass

    def join_channel(self, u_id, channel_id):
        pass

    def leave_channel(self, u_id, channel_id):
        pass

    def add_message(self, channel_id, message):
        pass

    def remove_message(self, message_id):
        pass

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
