'''
Using requests module to test channel functions
'''

import json
import time
import urllib.request
from urllib.error import HTTPError
import pytest

import urls
from error import AccessError, InputError
from http_helpers import (reset, register, login, logout,
                          message_send, channels_create,
                          channel_messages, channel_join, channel_leave,
                          channel_addowner, channel_removeowner,
                          message_remove, channels_list)

MESSAGE_BLOCK = 50

#Testing channel_messages
def test_channel_messages_empty(reset):
    '''
    Tests sending a request to get an empty messages list
    '''
    my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    with pytest.raises(HTTPError):
        channel_messages(my_token, channel_id, start=0)

def test_channel_messages_one_message(reset):
    '''
    Testing getting a list containing one message
    '''
    #register
    my_uid, my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')
    #create a channel
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    #send a message
    msg_id = message_send(my_token, channel_id, 'first message!')
    time_created = time.time()
    #get the messages
    messages, start, end = channel_messages(my_token, channel_id, start=0)
    #asserting
    assert messages[0]['message'] == 'first message!'
    assert messages[0]['message_id'] == msg_id
    assert messages[0]['channel_id'] == channel_id
    assert messages[0]['u_id'] == my_uid
    assert time_created - messages[0]['time_created'] < 1
    assert messages[0]['reacts'][0]['u_ids'] == []
    assert start == 0
    assert end == -1
    #logging out as next test requires logging in
    logout(my_token)

def test_channel_messages_two_messages():
    '''
    Testing sending another message to the server WITHOUT resetting
    '''
    my_token = login('z5236259@unsw.edu.au', '1231FFF!')[1]

    #getting the available channel and sending a message
    channel_id = channels_list(my_token)[0]['channel_id']
    msg_id = message_send(my_token, channel_id, 'second message!')
    time_created = time.time()
    #getting the messages
    messages, start, end = channel_messages(my_token, channel_id, start=0)
    #asserting
    assert messages[0]['message'] == 'second message!'
    assert messages[0]['message_id'] == msg_id
    assert time_created - messages[0]['time_created'] < 1
    assert messages[1]['message'] == 'first message!'
    assert start == 0
    assert end == -1

def test_channel_messages_more_than_fifty(reset):
    '''
    Testing sending over 50 messages and requesting the first 50
    '''
    my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    #create a channel
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    #sending the messages
    for i in range(51):
        message_send(my_token, channel_id, f"message {i}")
    #getting the messages
    messages, start, end = channel_messages(my_token, channel_id, start=0)
    #asserting
    assert len(messages) == MESSAGE_BLOCK
    assert messages[0]['message'] == 'message 50' #last message sent
    assert messages[-1]['message'] == 'message 1' #oldest message sent
    assert start == 0
    assert end == MESSAGE_BLOCK


def test_channel_messages_invalid_channel_id(reset):
    '''
    Testing calling the route with an invalid channel id
    '''
    my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    #create a channel
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    with pytest.raises(HTTPError):
        channel_messages(my_token, channel_id + 1, start=0)
    logout(my_token)

def test_channel_messages_invalid_token():
    '''
    Checking an invalid token raises an exception
    '''
    my_token = login('z5236259@unsw.edu.au', '1231FFF!')[1]
    #getting the available channel
    channel_id = channels_list(my_token)[0]['channel_id']
    #assertion
    with pytest.raises(HTTPError):
        channel_messages(my_token, channel_id, start=0)

#Testing channel_join
def test_channel_join_ok(reset):
    '''
    A valid request to join a channel
    '''
    owner_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    user_token = register('z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')[1]
    #create a channel
    channel_id = channels_create(owner_token, 'Yousifs Channel', is_public=True)
    channel_join(user_token, channel_id)
    message_send(user_token, channel_id, 'My first message!')

def test_channel_join_private(reset):
    '''
    An invalid request to join a private channel
    '''
    owner_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    user_token = register('z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')[1]
    #create a channel
    channel_id = channels_create(owner_token, 'Yousifs Channel', is_public=False)
    with pytest.raises(HTTPError):
        channel_join(user_token, channel_id)

def test_channel_join_invalid_token(reset):
    '''
    An invalid request with an invalid token
    '''
    owner_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    user_token = register('z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')[1]
    #create a channel
    channel_id = channels_create(owner_token, 'Yousifs Channel', is_public=False)
    with pytest.raises(HTTPError):
        channel_join(user_token + 'a', channel_id)

def test_channel_join_already_joined(reset):
    '''
    An invalid attempt to join an already joined channel
    '''
    owner_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    user_token = register('z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')[1]
    #create a channel
    channel_id = channels_create(owner_token, 'Yousifs Channel', is_public=True)
    channel_join(user_token, channel_id)
    with pytest.raises(HTTPError):
        channel_join(user_token, channel_id)
    #loggging out for next test
    logout(user_token)
    logout(owner_token)

#testing channel_leave
def test_channel_leave_ok():
    '''
    Testing leaving a channel
    '''
    user_token = login('z123456@unsw.edu.au', 'bananaboy!')[1]
    #getting the available channel
    channel_id = channels_list(user_token)[0]['channel_id']
    channel_leave(user_token, channel_id)
    #this means I can join once again without an issue
    channel_join(user_token, channel_id)

def test_channel_leave_not_a_member(reset):
    '''
    Invalid to leave a channel when not a member
    '''
    owner_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    user_token = register('z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')[1]
    #create a channel
    channel_id = channels_create(owner_token, 'Yousifs Channel', is_public=True)
    with pytest.raises(HTTPError):
        channel_leave(user_token, channel_id)

def test_channel_leave_only_member_to_private(reset):
    '''
    Invalid request to leave a private channel as the only member
    '''
    owner_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    #create a channel
    channel_id = channels_create(owner_token, 'Yousifs Channel', is_public=False)
    with pytest.raises(HTTPError):
        channel_leave(owner_token, channel_id)

def test_channel_leave_invalid_token(reset):
    '''
    Invalid request with an invalid token
    '''
    owner_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    user_token = register('z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')[1]
    #create a channel
    channel_id = channels_create(owner_token, 'Yousifs Channel', is_public=True)
    channel_join(user_token, channel_id)
    with pytest.raises(HTTPError):
        channel_leave(user_token + 'a', channel_id)

#testing channel_addowner
def test_channel_addowner_ok(reset):
    '''
    A valid request to add a  user as an owner to a channel
    '''
    owner_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    user_id, user_token = register('z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')
    #create a channel
    channel_id = channels_create(owner_token, 'Yousifs Channel', is_public=True)
    #make user owner
    channel_addowner(owner_token, channel_id, user_id)
    #send a generic message as an owner
    msg_id = message_send(owner_token, channel_id, 'owners message')
    #try to delete message
    message_remove(user_token, msg_id)

def test_channel_addowner_as_reg_member(reset):
    '''
    An Invalid request to add a user to a
    '''
    owner_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    user_id = register('z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')[0]
    imposer_token = register('z232332@unsw.edu.au', '1234151', 'Koko', 'Lime')[1]
    #create a channel
    channel_id = channels_create(owner_token, 'Yousifs Channel', is_public=True)
    channel_join(imposer_token, channel_id)   
    #assertion
    with pytest.raises(HTTPError):
        channel_addowner(imposer_token, channel_id, user_id)

def test_channel_addowner_already_owner(reset):
    '''
    Invalid request to add an owner as an owner
    '''
    owner_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    user_id = register('z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')[0]
    #create a channel
    channel_id = channels_create(owner_token, 'Yousifs Channel', is_public=True)
    #add owner
    channel_addowner(owner_token, channel_id, user_id)
    #add again..
    with pytest.raises(HTTPError):
        channel_addowner(owner_token, channel_id, user_id)

def test_channel_addowner_non_member(reset):
    '''
    An Invalid request to add a user to a
    '''
    owner_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    user_id = register('z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')[0]
    imposer_token = register('z232332@unsw.edu.au', '1234151', 'Koko', 'Lime')[1]
    #create a channel
    channel_id = channels_create(owner_token, 'Yousifs Channel', is_public=True)
    #assertion
    with pytest.raises(HTTPError):
        channel_addowner(imposer_token, channel_id, user_id)

def test_channel_addowner_invalid_token(reset):
    '''
    Invalid request <=> invalid token
    '''
    owner_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    user_id = register('z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')[0]
    #create a channel
    channel_id = channels_create(owner_token, 'Yousifs Channel', is_public=True)
    #assertion
    with pytest.raises(HTTPError):
        channel_addowner(owner_token + 'a', channel_id, user_id)

#testing channel_removeowner
def test_channel_removeowner_ok(reset):
    '''
    Valid request to remove an owner
    '''
    owner_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    user_id, user_token = register('z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')
    #create a channel
    channel_id = channels_create(owner_token, 'Yousifs Channel', is_public=True)
    #sending a message as owner
    msg_id = message_send(owner_token, channel_id, 'blabla')
    #adding then removing
    channel_addowner(owner_token, channel_id, user_id)
    channel_removeowner(owner_token, channel_id, user_id)
    try:
        message_remove(user_token, msg_id)
    except HTTPError:
        pass

def test_channel_removeowner_invalid_token(reset):
    '''
    Valid request to remove an owner
    '''
    owner_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    user_id = register('z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')[0]
    #create a channel
    channel_id = channels_create(owner_token, 'Yousifs Channel', is_public=True)
    #adding then removing
    channel_addowner(owner_token, channel_id, user_id)
    with pytest.raises(HTTPError):
        channel_removeowner(owner_token + 'a', channel_id, user_id)

def test_channel_removeowner_reg_member(reset):
    '''
    Invalid request to remove owner as non owner
    '''
    owner_id, owner_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')
    user_token = register('z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')[1]
    #create a channel
    channel_id = channels_create(owner_token, 'Yousifs Channel', is_public=True)
    #join channel
    channel_join(user_token, channel_id)
    with pytest.raises(HTTPError):
        channel_removeowner(user_token, channel_id, owner_id)

def test_channel_removeowner_already_not(reset):
    '''
    Invalid request to remove ownership from a non-owner
    '''
    owner_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    user_id, user_token = register('z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')
    #create a channel
    channel_id = channels_create(owner_token, 'Yousifs Channel', is_public=True)
    #join channel
    channel_join(user_token, channel_id)
    with pytest.raises(HTTPError):
        channel_removeowner(owner_token, channel_id, user_id)

def test_channel_removeowner_not_a_member(reset):
    '''
    Invalid request to remove ownership being a non-member
    '''
    owner_id, owner_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')
    user_token = register('z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')[1]
    #create a channel
    channel_id = channels_create(owner_token, 'Yousifs Channel', is_public=True)
    with pytest.raises(HTTPError):
        channel_removeowner(user_token, channel_id, owner_id)
