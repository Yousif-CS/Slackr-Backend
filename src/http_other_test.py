'''
HTTP tests for functions in other.py
'''

import pytest
import urls
import json
import urllib.request
from urllib.error import HTTPError
from http_helpers import reset, register, login, logout, userpermission_change, users_all, search, \
    channels_create, message_send, channel_messages, channel_join

# can change permission
def test_userpermission_change(reset):
    j_id, j_token = register("joshwang@gmail.com", "paris in the rain", "Josh", "Wang") # this user is the owner
    k_id, k_token = register("kenli@gmail.com", "pianoforte", "Ken", "Li") # normal member
    i_id, i_token = register("ianjacobs@hotmail.com", "ilovetrimesters", "Ian", "Jacobs") # normal member

    # Josh makes Ken an owner
    userpermission_change(j_token, k_id, 1)
    
    # Now Ken should be able to demote Josh to a normal member and promote Ian an owner
    userpermission_change(k_token, j_id, 2)
    userpermission_change(k_token, i_id, 1)

# u_id not a valid user
def test_userpermission_change_invalid_u_id(reset):
    j_id, j_token = register("joshwang@gmail.com", "paris in the rain", "Josh", "Wang")
    with pytest.raises(HTTPError):
        userpermission_change(j_token, j_id + 1, 1)
# permission_id not a valid permission
def test_user_permission_change_invalid_permission(reset):
    j_id, j_token = register("joshwang@gmail.com", "paris in the rain", "Josh", "Wang") # this user is the owner
    k_id, k_token = register("kenli@gmail.com", "pianoforte", "Ken", "Li") # normal member
    with pytest.raises(HTTPError):
        userpermission_change(j_token, k_id, 3)

# authorised user is not an owner
def test_userpermission_change_not_owner(reset):
    j_id, j_token = register("joshwang@gmail.com", "paris in the rain", "Josh", "Wang") # this user is the owner
    k_id, k_token = register("kenli@gmail.com", "pianoforte", "Ken", "Li") # normal member
    with pytest.raises(HTTPError):
        userpermission_change(k_token, j_id, 2)

# data missing
def test_user_permission_change_data_missing(reset):
    j_id, j_token = register("joshwang@gmail.com", "paris in the rain", "Josh", "Wang") # this user is the owner
    k_id, k_token = register("kenli@gmail.com", "pianoforte", "Ken", "Li") # normal member

    data = json.dumps({
        'token': j_token,
        'permission_id': 2
    }).encode()

    request = urllib.request.Request(urls.PERMISSION_CHANGE_URL, data=data, \
        method='POST', headers={'Content-Type': 'application/json'})

    with pytest.raises(HTTPError):
        urllib.request.urlopen(request)

# can produce a list of users
def test_users_all(reset):
    j_id, j_token = register("joshwang@gmail.com", "paris in the rain", "Josh", "Wang")
    k_id = register("kenli@gmail.com", "pianoforte", "Ken", "Li")[0]
    i_id = register("ianjacobs@hotmail.com", "ilovetrimesters", "Ian", "Jacobs")[0]
    h_id = register("harrypartridge@yahoo.com.au", "datascience", "Harry", "Partridge")[0]

    everyone = users_all(j_token)['users']
    assert len(everyone) == 4
    assert everyone[0]['u_id'] == j_id
    assert everyone[1]['u_id'] == k_id
    assert everyone[2]['u_id'] == i_id
    assert everyone[3]['u_id'] == h_id

# data missing
def test_users_all_data_missing(reset):
    j_token = register("joshwang@gmail.com", "paris in the rain", "Josh", "Wang")[1]
    register("kenli@gmail.com", "pianoforte", "Ken", "Li")
    with pytest.raises(HTTPError):
        urllib.request.urlopen(urls.USERS_ALL_URL)


# can search a variety of strings sent by different users in a multitude of channels of which the auth user is part
def test_search_1(reset):
    j_token = register("joshwang@gmail.com", "paris in the rain", "Josh", "Wang")[1]
    k_token = register("kenli@gmail.com", "pianoforte", "Ken", "Li")[1]
    i_token = register("ianjacobs@hotmail.com", "ilovetrimesters", "Ian", "Jacobs")[1]

    ch_id1 = channels_create(j_token, "channel1", True)
    ch_id2 = channels_create(k_token, "channel2", True)
    ch_id3 = channels_create(i_token, "channel3", True)

    channel_join(j_token, ch_id2)
    channel_join(k_token, ch_id3)

    message_send(j_token, ch_id1, "Cat get down!")
    message_send(k_token, ch_id2, "this is the category")
    message_send(i_token, ch_id3, "cataracts are bad for your eyes")
    message_send(j_token, ch_id2, "scathe hat bat shat in the lsadfkl")
    message_send(j_token, ch_id2, "token")
    message_send(k_token, ch_id3, "a;sdkjf;lasdjf;lj 3wioru cate")

    assert len(search(j_token, "cat")["messages"]) == 2
    assert len(search(k_token, "cat")["messages"]) == 4
    assert len(search(i_token, "cat")["messages"]) == 2

# empty query string possible
def test_search_empty(reset):
    j_token = register("joshwang@gmail.com", "paris in the rain", "Josh", "Wang")[1]
    ch_id = channels_create(j_token, "new_channel", True)
    message_send(j_token, ch_id, "First message")
    message_send(j_token, ch_id, "Second message")
    assert len(search(j_token, "")["messages"]) == 0

# query string too long
def test_search_query_str_too_long(reset):
    j_token = register("joshwang@gmail.com", "paris in the rain", "Josh", "Wang")[1]
    ch_id = channels_create(j_token, "new_channel", True)
    message_send(j_token, ch_id, "First message")
    message_send(j_token, ch_id, "Second message")

    with pytest.raises(HTTPError):
        search(j_token, "i"*1001)

# data missing
def test_search_data_missing(reset):
    j_token = register("joshwang@gmail.com", "paris in the rain", "Josh", "Wang")[1]
    ch_id = channels_create(j_token, "new_channel", True)
    message_send(j_token, ch_id, "First message")

    data = json.dumps({
        'token': j_token
    }).encode()

    request = urllib.request.Request(urls.SEARCH_URL, data=data, \
        method='GET', headers={'Content-Type': 'application/json'})
    
    with pytest.raises(HTTPError):
        urllib.request.urlopen(request)

# invalid token tests
def test_userpermission_change_invalid_token(reset):
    j_token = register("joshwang@gmail.com", "paris in the rain", "Josh", "Wang")[1]
    k_id = register("kenli@hotmail.com", "asd;fkljas;dfljklas;df", "Ken", "Li")[0]
    with pytest.raises(HTTPError):
        userpermission_change(j_token + 'x', k_id, 1)

def test_users_all_invalid_token(reset):
    j_token = register("joshwang@gmail.com", "paris in the rain", "Josh", "Wang")[1]
    register("kenli@hotmail.com", "asd;fkljas;dfljklas;df", "Ken", "Li")
    with pytest.raises(HTTPError):
        users_all(j_token + 'x')

def test_search_invalid_token(reset):
    j_token = register("joshwang@gmail.com", "paris in the rain", "Josh", "Wang")[1]
    ch_id = channels_create(j_token, "new_channel", True)
    message_send(j_token, ch_id, "First message")
    with pytest.raises(HTTPError):
        search(j_token + 'x', 'First')
