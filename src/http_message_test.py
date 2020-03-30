import pytest
import urls
import json
import urllib.request
from urllib.error import HTTPError

from http_helpers import reset, register, login, logout, \
    message_send, channel_messages, channels_create


def test_message_send_ok(reset):
    '''
    Testing sending a valid message by an authorised user
    '''
    a_token = register('admin@gmail.com', 'pass123456', 'Alan', 'Brown')[1]
    channel_id = channels_create(a_token, 'test_public', True)
    message_send(a_token, channel_id, 'test message')
    msg_list = channel_messages(a_token, channel_id, 0)[0]
    assert len(msg_list) == 1
    assert msg_list[0]['message'] == 'test message'
    logout(a_token)

def test_message_send_invalid_message():
    '''
    Testing sending an invalid message
    '''
    a_token = login('admin@gmail.com', 'pass123456')[1]
    with pytest.raises(HTTPError):
        message_send(a_token, 1, 'a' * 1001)

def test_message_send_invalid_token():
    '''
    Testing requesting with invalid token
    '''
    a_token = login('admin@gmail.com', 'pass123456')[1]
    with pytest.raises(HTTPError):
        message_send(a_token + 'x', 1, 'Hello world')

def test_message_send_not_in_channel():
    '''
    Testing requesting to send message when not in channel
    '''
    k_token = register('ken@gmail.com', 'kenis123', 'Ken', 'Li')[1]
    with pytest.raises(HTTPError):
        message_send(k_token, 1, 'Bad message')

