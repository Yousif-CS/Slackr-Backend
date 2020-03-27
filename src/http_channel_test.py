'''
Using requests module to test channel functions
'''

import json 
import requests
import pytest
import time

import urls
from http_helpers import (reset, register, login, message_send, channels_create, 
                        channel_messages, channels_list)
from error import AccessError, InputError

MESSAGE_BLOCK = 50

#Testing channel_messages
def test_channel_messages_empty(reset):
    '''
    Tests sending a request to get an empty messages list
    '''
    my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]

    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    with pytest.raises(InputError):
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
    assert messages[0]['time_created'] == time_created
    assert messages[0]['reacts'] == []
    assert start == 0
    assert end == -1

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
    assert messages[0]['time_created'] == time_created
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
        time.sleep(0.2)  #just so that we can see a difference in timestamps
    #getting the messages
    messages, start, end = channel_messages(my_token, channel_messages, start=0)
    #asserting
    assert len(messages) == MESSAGE_BLOCK
    assert messages[0]['message'] == 'message 50' #last message sent
    assert messages[-1]['message'] == 'message 0' #first message sent
    assert start == 0
    assert end == MESSAGE_BLOCK
