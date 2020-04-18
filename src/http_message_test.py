'''
HTTP tests for functions in message.py
'''
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-import
# pylint: disable=missing-function-docstring

import time
import json
import urllib.request
from urllib.error import HTTPError
import pytest #pylint: disable=import-error
import urls

from http_helpers import (reset, register, login, logout,
                          message_send, message_sendlater, channel_messages,
                          channels_create, message_react, message_unreact,
                          message_pin, message_unpin, channel_join,
                          channel_leave, search, message_edit, message_remove)


def test_message_send_ok(reset):
    '''
    Testing sending a valid message by an authorised user
    '''
    a_token = register('admin@gmail.com', 'pass123456', 'Alan', 'Brown')[1]
    channel_id = channels_create(a_token, 'test_public', True)
    message_send(a_token, channel_id, 'test message')
    msg_list = channel_messages(a_token, channel_id, 0)[0]
    assert len(msg_list) == 2 # hangman bot sends a message as well
    assert msg_list[0]['message'] == 'test message'
    logout(a_token)

def test_message_send_invalid_message():
    '''
    Testing sending an invalid message
    '''
    a_token = login('admin@gmail.com', 'pass123456')[1]
    with pytest.raises(HTTPError):
        message_send(a_token, 1, 'a' * 1001)
    logout(a_token)

def test_message_send_invalid_token():
    '''
    Testing requesting with invalid token
    '''
    a_token = login('admin@gmail.com', 'pass123456')[1]
    with pytest.raises(HTTPError):
        message_send(a_token + 'x', 1, 'Hello world')
    logout(a_token)

def test_message_send_not_in_channel():
    '''
    Testing requesting to send message when not in channel
    '''
    k_token = register('ken@gmail.com', 'kenis123', 'Ken', 'Li')[1]
    with pytest.raises(HTTPError):
        message_send(k_token, 1, 'Bad message')
    logout(k_token)

# testing message sendlater
def test_message_sendlater_ok(reset):
    '''
    Testing message send later request
    '''
    a_token = register('admin@gmail.com', 'pass123456', 'Alan', 'Brown')[1]
    channel_id = channels_create(a_token, 'test_public', True)

    msg_id = message_sendlater(a_token, channel_id, 'sending later', time.time() + 3)
    assert msg_id == 2 # hangman sends the first message -> next available id is 2
    logout(a_token)

def test_message_sendlater_badtime():
    '''
    Testing message send later request with time_sent in the past
    '''
    a_token = login('admin@gmail.com', 'pass123456')[1]
    with pytest.raises(HTTPError):
        message_sendlater(a_token, 1, 'sending later', time.time() - 0.01)
    logout(a_token)

def test_message_sendlater_threading(reset):
    '''
    Testing other requests can be processed concurrently without disturbing sendlater
    '''
    k_token = register('ken@gmail.com', 'kenis123', 'Ken', 'Li')[1]
    channel_id = channels_create(k_token, 'test_public', True)
    message_sendlater(k_token, channel_id, 'sending later', time.time() + 1)
    message_send(k_token, channel_id, 'test message0')
    message_send(k_token, channel_id, 'test message1')
    time.sleep(2)
    msg_list = channel_messages(k_token, channel_id, 0)[0]
    assert len(msg_list) == 4 # hangman sends a message as well 
    assert msg_list[0]['message'] == 'sending later'
    logout(k_token)

def test_message_sendlater_not_in_channel(reset):
    '''
    Testing requesting to send message later when not in channel
    '''
    a_token = register('admin@gmail.com', 'pass123456', 'Alan', 'Brown')[1]
    channel_id = channels_create(a_token, 'test_public', True)
    k_token = register('ken@gmail.com', 'kenis123', 'Ken', 'Li')[1]
    with pytest.raises(HTTPError):
        message_sendlater(k_token, channel_id, 'Bad message', time.time() + 1)
    logout(a_token)

def test_message_sendlater_invalid_token():
    '''
    Testing requesting with invalid token
    '''
    a_token = login('admin@gmail.com', 'pass123456')[1]
    channel_id = channels_create(a_token, 'test_public', True)
    with pytest.raises(HTTPError):
        message_sendlater(a_token + 'x', channel_id, 'Hello world', time.time() + 1)
    logout(a_token)

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
        message_react(k_token, 1, 1)
    logout(k_token)

def test_message_react_nonexistent_message_id():
    a_token = login('admin@gmail.com', 'pass123456')[1]
    with pytest.raises(HTTPError):
        message_react(a_token, 2222, 1)
    logout(a_token)

def test_message_react_invalid_react():
    a_token = login('admin@gmail.com', 'pass123456')[1]
    msg1_id = message_send(a_token, 1, 'a second test message')

    with pytest.raises(HTTPError):
        message_react(a_token, msg1_id, 2)
    logout(a_token)

def test_message_react_already_reacted():
    a_token = login('admin@gmail.com', 'pass123456')[1]
    channel_id_priv = channels_create(a_token, 'test_private', False)
    msg1_id = message_send(a_token, channel_id_priv, 'test message please react')
    message_react(a_token, msg1_id, 1)

    with pytest.raises(HTTPError):
        message_react(a_token, msg1_id, 1)
    logout(a_token)

def test_message_react_invalid_token():
    a_token = login('admin@gmail.com', 'pass123456')[1]

    with pytest.raises(HTTPError):
        message_react(a_token + 'x', 1, 1)
    logout(a_token)

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
    logout(c_token)

def test_message_unreact_invalid_react():
    a_token = login('admin@gmail.com', 'pass123456')[1]

    with pytest.raises(HTTPError):
        message_unreact(a_token, 0, 2)
    logout(a_token)

def test_message_unreact_no_existing_react(reset):
    a_token = register('admin@gmail.com', 'pass123456', 'Admin', 'Heeblo')[1]
    channels_create(a_token, 'test_public', True)
    msg0_id = message_send(a_token, 1, 'I am new here.')

    with pytest.raises(HTTPError):
        message_unreact(a_token, msg0_id, 1)
    logout(a_token)

def test_message_unreact_invalid_token():
    a_token = login('admin@gmail.com', 'pass123456')[1]

    with pytest.raises(HTTPError):
        message_react(a_token + 'x', 0, 1)
    logout(a_token)

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

def test_message_pin_owner_pins_user():
    a_token = login('admin@gmail.com', 'pass123456')[1]
    k_token = register('ken@gmail.com', 'kenis123', 'Ken', 'Li')[1]
    channel_join(k_token, 1)
    msg1_id = message_send(k_token, 1, 'User message')
    # user a pins user k's message
    message_pin(a_token, msg1_id)

    msg_list = channel_messages(a_token, 1, 0)[0]
    assert msg_list[0]['is_pinned'] and msg_list[1]['is_pinned']
    logout(a_token)
    logout(k_token)

def test_message_pin_invalid_message_id():
    a_token = login('admin@gmail.com', 'pass123456')[1]
    with pytest.raises(HTTPError):
        message_pin(a_token, 35)
    logout(a_token)

def test_message_pin_not_owner_tries():
    c_token = register('cen@gmail.com', 'ssap12652', 'Chen', 'Bee')[1]
    channel_join(c_token, 1)
    msg1_id = message_send(c_token, 1, 'My own message')

    with pytest.raises(HTTPError):
        message_pin(c_token, msg1_id)
    logout(c_token)

def test_message_pin_already_pinned():
    # recall from first test, admin already pinned their own message
    a_token = login('admin@gmail.com', 'pass123456')[1]
    with pytest.raises(HTTPError):
        message_pin(a_token, 2)
    logout(a_token)

def test_message_pin_not_member():
    c_token = login('cen@gmail.com', 'ssap12652')[1]
    channel_leave(c_token, 1)
    with pytest.raises(HTTPError):
        message_pin(c_token, 1)
    logout(c_token)

# testing message_unpin
def test_message_unpin_owner(reset):
    a_token = register('admin@gmail.com', 'pass123456', 'Admin', 'Heeblo')[1]
    channel_id = channels_create(a_token, 'test_public', True)
    msg0_id = message_send(a_token, channel_id, 'Pin this message')
    # pins the message
    message_pin(a_token, msg0_id)
    message_unpin(a_token, msg0_id)
    msg_list = channel_messages(a_token, channel_id, 0)[0]

    assert not msg_list[0]['is_pinned']
    logout(a_token)


def test_message_unpin_invalid_message(reset):
    a_token = register('admin@gmail.com', 'pass123456', 'Admin', 'Heeblo')[1]
    channel_id = channels_create(a_token, 'test_public', True)
    msg0_id = message_send(a_token, channel_id, 'Pin this message')
    # pins the message
    message_pin(a_token, msg0_id)

    with pytest.raises(HTTPError):
        message_unpin(a_token, msg0_id + 1)
    logout(a_token)

def test_message_unpin_not_channel_owner(reset):
    a_token = register('admin@gmail.com', 'pass123456', 'Admin', 'Heeblo')[1]
    channel_id = channels_create(a_token, 'test_public', True)
    msg0_id = message_send(a_token, channel_id, 'Pin this message')
    # pins the message
    message_pin(a_token, msg0_id)

    # make another user who is part of channel but not owner nor slackr owner
    u_token = register('user@gmail.com', 'usersweakpw', 'Bob', 'Builder')[1]
    channel_join(u_token, channel_id)

    with pytest.raises(HTTPError):
        message_unpin(u_token, msg0_id)
    logout(a_token)

def test_message_unpin_not_pinned(reset):
    a_token = register('admin@gmail.com', 'pass123456', 'Admin', 'Heeblo')[1]
    channel_id = channels_create(a_token, 'test_public', True)
    msg0_id = message_send(a_token, channel_id, 'Not pinned message')

    with pytest.raises(HTTPError):
        message_unpin(a_token, msg0_id)
    logout(a_token)

def test_message_unpin_slackr_owner_not_in_channel(reset):
    a_token = register('admin@gmail.com', 'pass123456', 'Admin', 'Heeblo')[1]
    k_token = register('ken@gmail.com', 'kenis123', 'Ken', 'Li')[1]
    # ken creates a channel
    k_channel_id = channels_create(k_token, 'test_public', True)
    msg0_id = message_send(k_token, k_channel_id, 'Kens message in his channel')
    message_pin(k_token, msg0_id)
    # admin unpins the message sent by ken
    message_unpin(a_token, msg0_id)

    msg_list = channel_messages(k_token, k_channel_id, 0)[0]
    assert not msg_list[0]['is_pinned']
    logout(a_token)
    logout(k_token)

def test_message_unpin_user_not_in_channel():
    c_token = register('cen@gmail.com', 'ssap12652', 'Chen', 'Bee')[1]

    with pytest.raises(HTTPError):
        message_unpin(c_token, 1)
    logout(c_token)

def test_message_unpin_invalid_token():
    a_token = login('admin@gmail.com', 'pass123456')[1]
    with pytest.raises(HTTPError):
        message_unpin(a_token + 'x', 1)
    logout(a_token)

# testing message_remove
def test_message_remove_own(reset):
    '''
    Testing removing a valid message by a valid authorised user
    '''
    a_token = register('admin@gmail.com', 'pass123456', 'Alan', 'Brown')[1]
    channel_id = channels_create(a_token, 'test_public', True)
    msg0_id = message_send(a_token, channel_id, 'test message to be removed')
    # check list is now empty after removal
    message_remove(a_token, msg0_id)
    message_send(a_token, channel_id, 'new_test_message')
    msg_list = channel_messages(a_token, channel_id, 0)[0]
    assert len(msg_list) == 2 # hangman bot sends a message as well..
    assert msg_list[0]['message'] == 'new_test_message'
    logout(a_token)

def test_message_remove_twice(reset):
    a_token = register('admin@gmail.com', 'pass123456', 'Alan', 'Brown')[1]
    channel_id = channels_create(a_token, 'test_public', True)
    msg0_id = message_send(a_token, channel_id, 'test message to be removed')

    message_remove(a_token, msg0_id)

    with pytest.raises(HTTPError):
        message_remove(a_token, 0)
    logout(a_token)

def test_message_remove_slackr_owner(reset):
    # slackr owner
    a_token = register('admin@gmail.com', 'pass123456', 'Alan', 'Brown')[1]
    k_token = register('ken@gmail.com', 'kenis123', 'Ken', 'Li')[1]
    # ken creates a channel
    channel_id = channels_create(k_token, 'test_public', True)
    msg0_id = message_send(k_token, channel_id, 'test message in ken channel')
    message_send(k_token, channel_id, 'test message2 in ken channel')

    message_remove(a_token, msg0_id)
    msg_list = channel_messages(k_token, channel_id, 0)[0]
    assert len(msg_list) == 2 # hangman bot sends a message at the start
    assert msg_list[0]['message'] == 'test message2 in ken channel'
    # unremoved message (2nd one sent) retains its ID
    assert msg_list[0]['message_id'] == 3 # hangman bot sends the first msg with id 1

    logout(a_token)
    logout(k_token)

def test_message_remove_regular_user_not_in_channel():
    c_token = register('cen@gmail.com', 'ssap12652', 'Chen', 'Bee')[1]
    with pytest.raises(HTTPError):
        message_remove(c_token, 2)
    logout(c_token)

def test_message_remove_invalid_token():
    a_token = login('admin@gmail.com', 'pass123456')[1]
    with pytest.raises(HTTPError):
        message_remove(a_token + 'x', 2)
    logout(a_token)

# testing message_edit

# can edit a message
def test_message_edit(reset):
    j_token = register("joshwang@gmail.com", "1234566", "Josh", "Wang")[1]
    ch_id = channels_create(j_token, "new_channel", True)

    msg_id1 = message_send(j_token, ch_id, "This is the first message before any editing.")
    msg_id2 = message_send(j_token, ch_id, "This is another message")
    assert len(search(j_token, "message")["messages"]) == 2

    message_edit(j_token, msg_id1, "Hurricane")
    assert len(search(j_token, "message")["messages"]) == 1
    assert search(j_token, "message")["messages"][0]["message_id"] == msg_id2
    assert len(search(j_token, "Hurr")["messages"]) == 1
    assert search(j_token, "Hurr")["messages"][0]["message_id"] == msg_id1

# deletes a message edited to empty
def test_message_edit_delete_empty(reset):
    j_token = register("joshwang@gmail.com", "1234566", "Josh", "Wang")[1]
    ch_id = channels_create(j_token, "new_channel", True)

    message_send(j_token, ch_id, "This is the first message before any editing.")
    msg_id2 = message_send(j_token, ch_id, "This is another message")

    message_edit(j_token, msg_id2, "")
    assert len(search(j_token, "message")["messages"]) == 1

# reject if message editor was not the message sender and is not an owner
def test_message_edit_reject_permission(reset):
    j_token = register("joshwang@gmail.com", "1234566", "Josh", "Wang")[1]
    k_token = register("ken@yahoo.com", "jludagsfhjkliopasdf", "Ken", "Li")[1]
    i_token = register("ian@jacobs.com", "aslkdfjwe", "Ian", "Jacobs")[1]
    l_token = register("lloyd@doublel.au", "ajsoqefdas", "Lloyd", "Freeman")[1]

    ch_id = channels_create(k_token, "new_channel", True)
    channel_join(i_token, ch_id)
    channel_join(l_token, ch_id)

    msg_id = message_send(l_token, ch_id, "This is a message")

    message_edit(j_token, msg_id, "Josh is a slack owner and can edit")
    message_edit(k_token, msg_id, "Ken is a channel owner and can edit")
    message_edit(l_token, msg_id, "Lloyd wrote the message and cand edit")

    with pytest.raises(HTTPError):
        message_edit(i_token, msg_id, "Ian was not involved and cannot edit for once")
