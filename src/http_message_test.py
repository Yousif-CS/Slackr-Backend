import pytest
import time
import urls
import json
import urllib.request
from urllib.error import HTTPError

from http_helpers import reset, register, login, logout, \
    message_send, message_sendlater, channel_messages, channels_create, \
    message_react, message_unreact, message_pin, message_unpin, \
    channel_join, channel_leave


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


# testing message sendlater
def test_message_sendlater_ok(reset):
    '''
    Testing message send later request
    '''
    a_token = register('admin@gmail.com', 'pass123456', 'Alan', 'Brown')[1]
    channel_id = channels_create(a_token, 'test_public', True)

    msg_id = message_sendlater(a_token, channel_id, 'sending later', time.time() + 0.01)
    assert msg_id == 0

def test_message_sendlater_badtime():
    '''
    Testing message send later request with time_sent in the past
    '''
    a_token = login('admin@gmail.com', 'pass123456')[1]
    with pytest.raises(HTTPError):
        message_sendlater(a_token, 1, 'sending later', time.time() - 0.01)

def test_message_sendlater_threading(reset):
    '''
    Testing other requests can be processed concurrently without disturbing sendlater
    '''
    k_token = register('ken@gmail.com', 'kenis123', 'Ken', 'Li')[1]
    channel_id = channels_create(k_token, 'test_public', True)
    msg_id = message_sendlater(k_token, channel_id, 'sending later', time.time() + 1)
    message_send(k_token, channel_id, 'test message0')
    message_send(k_token, channel_id, 'test message1')
    time.sleep(1)
    msg_list = channel_messages(k_token, channel_id, 0)[0]
    assert len(msg_list) == 3
    assert msg_list[0]['message'] == 'sending later'

def test_message_sendlater_not_in_channel(reset):
    '''
    Testing requesting to send message later when not in channel
    '''
    a_token = register('admin@gmail.com', 'pass123456', 'Alan', 'Brown')[1]
    channel_id = channels_create(a_token, 'test_public', True)
    k_token = register('ken@gmail.com', 'kenis123', 'Ken', 'Li')[1]
    with pytest.raises(HTTPError):
        message_sendlater(k_token, channel_id, 'Bad message', time.time() + 1)

def test_message_sendlater_invalid_token():
    '''
    Testing requesting with invalid token
    '''
    a_token = login('admin@gmail.com', 'pass123456')[1]
    channel_id = channels_create(a_token, 'test_public', True)
    with pytest.raises(HTTPError):
        message_sendlater(a_token + 'x', channel_id, 'Hello world', time.time() + 1)

# testing message react
def test_message_react_ok(reset):
    a_id, a_token = register('admin@gmail.com', 'pass123456', 'Alan', 'Brown')
    channel_id = channels_create(a_token, 'test_public', True)
    msg0_id = message_send(a_token, channel_id, 'test message please react')
    message_react(a_token, msg0_id, 1)
    msg_list = channel_messages(a_token, channel_id, 0)[0]
 
    assert a_id in msg_list[0]['reacts'][0]['u_ids']
    assert msg_list[0]['reacts'][0]['react_id'] == 1
    logout(a_token)

def test_message_react_not_in_channel():
    k_token = register('ken@gmail.com', 'kenis123', 'Ken', 'Li')[1]
    with pytest.raises(HTTPError):
        message_react(k_token, 0, 1)

def test_message_react_nonexistent_message_id():
    a_token = login('admin@gmail.com', 'pass123456')[1]
    with pytest.raises(HTTPError):
        message_react(a_token, 2222, 1)

def test_message_react_invalid_react():
    a_token = login('admin@gmail.com', 'pass123456')[1]
    msg1_id = message_send(a_token, 1, 'a second test message')

    with pytest.raises(HTTPError):
        message_react(a_token, msg1_id, 2)

def test_message_react_already_reacted():
    a_token = login('admin@gmail.com', 'pass123456')[1]
    channel_id_priv = channels_create(a_token, 'test_private', False)
    msg1_id = message_send(a_token, channel_id_priv, 'test message please react')
    message_react(a_token, msg1_id, 1)

    with pytest.raises(HTTPError):
        message_react(a_token, msg1_id, 1)

def test_message_react_invalid_token():
    a_token = login('admin@gmail.com', 'pass123456')[1]

    with pytest.raises(HTTPError):
        message_react(a_token + 'x', 1, 1)

# testing message_unreact
def test_message_unreact_own(reset):
    a_token = register('admin@gmail.com', 'pass123456', 'Alan', 'Brown')[1]
    channel_id = channels_create(a_token, 'test_public', True)
    msg0_id = message_send(a_token, channel_id, 'test message please react')
    message_react(a_token, msg0_id, 1)
    # unreacting
    message_unreact(a_token, msg0_id, 1)
    msg_list = channel_messages(a_token, channel_id, 0)[0]
    assert msg_list[0]['reacts'][0]['u_ids'] == []
    logout(a_token)

def test_message_unreact_not_in_channel():
    c_token = register('cen@gmail.com', 'ssap12652', 'Chen', 'Bee')[1]
    channel_join(c_token, 1)
    msg1_id = message_send(c_token, 1, 'I am new here.')
    message_react(c_token, msg1_id, 1)
    channel_leave(c_token, 1)
    with pytest.raises(HTTPError):
        message_unreact(c_token, 1, 1)

def test_message_unreact_invalid_react():
    a_token = login('admin@gmail.com', 'pass123456')[1]

    with pytest.raises(HTTPError):
        message_unreact(a_token, 0, 2)

def test_message_unreact_no_existing_react(reset):
    a_token = register('admin@gmail.com', 'pass123456', 'Admin', 'Heeblo')[1]
    channels_create(a_token, 'test_public', True)
    msg0_id = message_send(a_token, 1, 'I am new here.')

    with pytest.raises(HTTPError):
        message_unreact(a_token, msg0_id, 1)

def test_message_unreact_invalid_token():
    a_token = login('admin@gmail.com', 'pass123456')[1]

    with pytest.raises(HTTPError):
        message_react(a_token + 'x', 0, 1)

# testing message_pin
def test_message_pin_owner(reset):
    a_token = register('admin@gmail.com', 'pass123456', 'Admin', 'Heeblo')[1]
    channel_id = channels_create(a_token, 'test_public', True)
    msg0_id = message_send(a_token, channel_id, 'Pin this message')
    # pins the message
    message_pin(a_token, msg0_id)
    msg_list = channel_messages(a_token, channel_id, 0)[0]

    assert msg_list[0]['is_pinned']
    logout(a_token)

def test_message_pin_invalid_message_id():
    a_token = login('admin@gmail.com', 'pass123456')[1]
    with pytest.raises(HTTPError):
        message_pin(a_token, 35)

def test_message_pin_not_owner_tries():
    c_token = register('cen@gmail.com', 'ssap12652', 'Chen', 'Bee')[1]
    channel_join(c_token, 1)
    msg1_id = message_send(c_token, 1, 'My own message')

    with pytest.raises(HTTPError):
        message_pin(c_token, msg1_id)

def test_message_pin_already_pinned():
    # recall from first test, admin already pinned their own message
    a_token = login('admin@gmail.com', 'pass123456')[1]
    with pytest.raises(HTTPError):
        message_pin(a_token, 1)

def test_message_pin_not_member():
    c_token = login('cen@gmail.com', 'ssap12652')[1]
    channel_leave(c_token, 1)
    with pytest.raises(HTTPError):
        message_pin(c_token, 1)

# testing message_unpin

# testing message_remove
