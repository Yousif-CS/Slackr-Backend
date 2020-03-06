# TODO: import more modules / functions as needed 

from message import message_send, message_remove
from error import AccessError, InputError
from auth import auth_login, auth_register
from channel import channel_messages, channel_join
from channels import channels_create
import pytest

# reminders: white space / empty messages? 
# invalid user token? throws Exception?

@pytest.fixture
def make_user_ab():
    user_ab = auth_register("alice@gmail.com", "stronkpassword123", "Alice", "Bee")
    return user_ab

@pytest.fixture
def make_user_cd():
    user_cd = auth_register("charlie@gmail.com", "comp1531pass", "Charlie", "Dee")
    return user_cd

@pytest.fixture
def create_public_channel(make_user_ab):
    user_ab = make_user_ab
    channel_id = channels_create(user_ab['token'], 'test_channel_public', True)    
    return (channel_id, user_ab)

@pytest.fixture
def create_private_channel(make_user_ab):
    user_ab = make_user_ab
    channel_id = channels_create(user_ab['token'], 'test_channel_private', False) 
    return (channel_id, user_ab)
    
'''------------------testing message_send--------------------'''
# inputs: (token, channel_id, message); output: {message_id}

# testing if an authorised user who is part of a channel can send messages correctly
# using channel_messages to check 
def test_message_send_correct_output(create_public_channel):
    new_public_channel, user_ab = create_public_channel
    # user_ab sends a message on the public channel
    msg1 = message_send(user_ab['token'], new_public_channel['channel_id'], "Hello world!")
    msg_view = channel_messages(user_ab['token'], new_public_channel['channel_id'], 0)
    first_msg = msg_view['messages'][0]     # dictionary; msg_view is a dictionary of list of dictionaries
    assert first_msg['message_id'] == msg1['message_id']
    assert first_msg['u_id'] == user_ab['u_id']
    assert first_msg['message'] == 'Hello world!'

# check type of message_id to be int and that user messages' message_id's are unique 
def test_message_send_type_id(create_public_channel):
    new_public_channel, user_ab = create_public_channel
    # user_ab sends a message on the public channel
    msg1 = message_send(user_ab['token'], new_public_channel['channel_id'], "Message1")
    msg2 = message_send(user_ab['token'], new_public_channel['channel_id'], "Message2")
    assert type(msg1['message_id']) == type(msg2['message_id']) == int
    assert msg1['message_id'] != msg2['message_id']

# testing that duplicate messages (messages with identical strings) are processed correctly
def test_message_send_duplicate_msgs(create_public_channel, make_user_cd):
    new_public_channel, user_ab = create_public_channel
    user_cd = make_user_cd
    # user_cd joins the channel 
    channel_join(user_ab['token'], new_public_channel['channel_id'])
    msg1_ab = message_send(user_ab['token'], new_public_channel['channel_id'], "I am part of this channel")
    msg2_cd = message_send(user_cd['token'], new_public_channel['channel_id'], "I am part of this channel")
    # retrieving messages
    msgs_view = channel_messages(user_ab['token'], new_public_channel['channel_id'], 0)
    first_msg = msgs_view['messages'][0]
    second_msg = msgs_view['messages'][1]
    assert first_msg['message'] == second_msg['message']
    assert first_msg['message_id'] != second_msg['message_id']
    
# testing that messages of any length (from 0 to 1000 characters) are allowed but any longer strings will throw InputError
def test_message_send_msg_good(create_public_channel):
    pass

# testing for AccessError: when user is not part of a channel 
# -> when the channel_id is not one where the user has joined? 

# testing for Exception: when channel_id is invalid


'''------------------testing message_remove--------------------'''

# reminder:
# 