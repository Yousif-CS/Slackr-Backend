# TODO: import more modules / functions as needed 
import pytest
import message
from error import AccessError, InputError

# reminders: white space / empty messages? 
# invalid user token? throws Exception?

'''------------------testing message_send--------------------'''
# inputs: (token, channel_id, message); output: {message_id}

# testing if an authorised user who is part of a channel can send messages correctly
# using channel_messages to check 

# testing for uniqueness of message_id
# check type of message_id to be int
# and that two messages sent in succession in the same channel have different message_id
# duplicate messages 

# testing that messages of any length (from 0 to 1000 characters) are allowed but any longer strings will throw InputError

# testing for AccessError: when user is not part of a channel 
# -> when the channel_id is not one where the user has joined? 

# testing for Exception: when channel_id is invalid


'''------------------testing message_remove--------------------'''

# reminder:
# 