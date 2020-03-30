'''
HTTP tests for functions in message.py
'''
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-import
import json
import urllib.request
from urllib.error import HTTPError
import pytest
import urls
from http_helpers import (reset, register, login, logout,
                          userpermission_change, search,
                          channels_create, message_send,
                          channel_messages, channel_join,
                          message_edit)

# can edit a message
def test_message_edit(reset):
    j_id, j_token = register("joshwang@gmail.com", "1234566", "Josh", "Wang")
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
    j_id, j_token = register("joshwang@gmail.com", "1234566", "Josh", "Wang")
    ch_id = channels_create(j_token, "new_channel", True)

    msg_id1 = message_send(j_token, ch_id, "This is the first message before any editing.")
    msg_id2 = message_send(j_token, ch_id, "This is another message")

    message_edit(j_token, msg_id2, "")
    assert len(search(j_token, "message")["messages"]) == 1

# reject if message editor was not the message sender and is not an owner
def test_message_edit_reject_permission(reset):
    j_id, j_token = register("joshwang@gmail.com", "1234566", "Josh", "Wang")
    k_id, k_token = register("ken@yahoo.com", "jludagsfhjkliopasdf", "Ken", "Li")
    i_id, i_token = register("ian@jacobs.com", "aslkdfjwe", "Ian", "Jacobs")
    l_id, l_token = register("lloyd@doublel.au", "ajsoqefdas", "Lloyd", "Freeman")

    ch_id = channels_create(k_token, "new_channel", True)
    channel_join(i_token, ch_id)
    channel_join(l_token, ch_id)

    msg_id = message_send(l_token, ch_id, "This is a message")

    message_edit(j_token, msg_id, "Josh is a slack owner and can edit")
    message_edit(k_token, msg_id, "Ken is a channel owner and can edit")
    message_edit(l_token, msg_id, "Lloyd wrote the message and cand edit")

    with pytest.raises(HTTPError):
        message_edit(i_token, msg_id, "Ian was not involved and cannot edit for once")
