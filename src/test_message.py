# TODO: import more modules / functions as needed 

from message import message_send, message_remove
from error import AccessError, InputError
from auth import auth_login, auth_register
from channel import channel_messages, channel_join, channel_invite, channel_leave
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
# 1. messages with white space and symbols, as long as length is under 1000 characters
# 2. messages that are 0 length 
def test_message_send_msg_good(create_public_channel):
    new_public_channel, user_ab = create_public_channel
    msg1 = message_send(user_ab['token'], new_public_channel['channel_id'], "awf;lk#5)(*#&                #W*%*@#&(hi")
    msg2 = message_send(user_ab['token'], new_public_channel['channel_id'], "m" * 1000)
    msg3 = message_send(user_ab['token'], new_public_channel['channel_id'], "")

    msgs_view = channel_messages(user_ab['token'], new_public_channel['channel_id'], 0)
    # checking that all the above messages sent successfully
    assert len(msgs_view['messages']) == 3

# testing for InputError when message length exceeds 1000 characters
# 1. All symbols
# 2. All white spaces
# 3. a mixture of characters
def test_message_send_msg_bad_symbols(create_public_channel): 
    new_public_channel, user_ab = create_public_channel
    with pytest.raises(InputError):
        message_send(user_ab['token'], new_public_channel['channel_id'], "b" * 1001)

def test_message_send_msg_bad_spaces(create_public_channel): 
    new_public_channel, user_ab = create_public_channel
    with pytest.raises(InputError):
        message_send(user_ab['token'], new_public_channel['channel_id'], " " * 1001)

def test_message_send_msg_bad_message(create_public_channel): 
    new_public_channel, user_ab = create_public_channel
    with pytest.raises(InputError):
        message_send(user_ab['token'], new_public_channel['channel_id'], "message&3." * 500 + " " * 400 + "loong" * 50)

# testing for AccessError: when user is not part of a channel 
def test_message_send_not_part_of_channel(create_private_channel, make_user_cd):
    # user_ab creates a private channel but does not add user_cd to it
    new_private_channel, user_ab = create_private_channel
    user_cd = make_user_cd

    with pytest.raises(AccessError):
        message_send(user_cd['token'], new_private_channel['channel_id'], "fomo")

# testing for AccesError: when previous user/owner of channel leaves the channel and attempts to send message
def test_message_send_owner_removed_send(create_private_channel, make_user_cd):
    new_private_channel, user_ab = create_private_channel
    user_cd = make_user_cd
    # user_ab ads user_cd to the channel
    channel_invite(user_ab['token'], new_private_channel['channel_id'], user_cd['u_id'])
    # user_ab then leaves the channel
    channel_leave(user_ab['token'], new_private_channel['channel_id'])
    
    with pytest.raises(AccessError):
        message_send(user_ab['token'], new_private_channel['channel_id'], "I left")


# testing for Exception: when channel_id is invalid and the channel does not actually exist
def test_message_send_channel_not_found(make_user_ab):
    user_ab = make_user_ab
    
    with pytest.raises(Exception):
        message_send(user_ab['token'], 22222, "Hello world!")

'''------------------testing message_remove--------------------'''

# reminder:
# 