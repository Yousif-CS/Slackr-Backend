'''
HTTP tests for functions in other.py
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
                          userpermission_change, user_remove, users_all,
                          search, channels_create, message_send, 
                          channel_messages, channel_join, channel_details)

# can change permission


def test_userpermission_change(reset):
    '''
    Change the permissions of another user (being the admin)
    '''
    # this user is the owner
    j_id, j_token = register("joshwang@gmail.com",
                             "paris in the rain", "Josh", "Wang")
    k_id, k_token = register(
        "kenli@gmail.com", "pianoforte", "Ken", "Li")  # normal member
    i_id = register(
        "ianjacobs@hotmail.com", "ilovetrimesters", "Ian", "Jacobs")[0]  # normal member

    # Josh makes Ken an owner
    userpermission_change(j_token, k_id, 1)

    # Now Ken should be able to demote Josh to a normal member and promote Ian an owner
    userpermission_change(k_token, j_id, 2)
    userpermission_change(k_token, i_id, 1)

# u_id not a valid user


def test_userpermission_change_invalid_u_id(reset):
    '''
    invalid request with invalid u_id
    '''
    j_id, j_token = register("joshwang@gmail.com",
                             "paris in the rain", "Josh", "Wang")
    with pytest.raises(HTTPError):
        userpermission_change(j_token, j_id + 1, 1)


def test_user_permission_change_invalid_permission(reset):
    '''
    permission_id not a valid permission
    '''
    # this user is the owner
    j_token = register("joshwang@gmail.com",
                       "paris in the rain", "Josh", "Wang")[1]
    k_id = register(
        "kenli@gmail.com", "pianoforte", "Ken", "Li")[0]  # normal member
    with pytest.raises(HTTPError):
        userpermission_change(j_token, k_id, 3)

# authorised user is not an owner


def test_userpermission_change_not_owner(reset):
    '''
    Invalid request where a person who is not an admin tries request change
    '''
    # this user is the owner
    j_id = register("joshwang@gmail.com",
                    "paris in the rain", "Josh", "Wang")[0]
    k_token = register(
        "kenli@gmail.com", "pianoforte", "Ken", "Li")[1]  # normal member
    with pytest.raises(HTTPError):
        userpermission_change(k_token, j_id, 2)

# data missing


def test_user_permission_change_data_missing(reset):
    '''
    test sending an incomplete request
    '''
    # this user is the owner
    j_token = register("joshwang@gmail.com",
                       "paris in the rain", "Josh", "Wang")[1]
    register("kenli@gmail.com", "pianoforte", "Ken", "Li")  # normal member

    data = json.dumps({
        'token': j_token,
        'permission_id': 2
    }).encode()

    request = urllib.request.Request(urls.PERMISSION_CHANGE_URL, data=data,
                                     method='POST', headers={'Content-Type': 'application/json'})

    with pytest.raises(HTTPError):
        urllib.request.urlopen(request)


def test_user_remove_invalid_token(reset):
    '''
    test sending an invalid token
    '''
    _, token = register('yousif@gmail.com', 'HelloWorld', 'Yousif', 'Wang')
    u_id, _ = register('josh@gmail.com', 'HelloWorld123', 'Josh', 'Wang')
    with pytest.raises(HTTPError):
        user_remove(token + 'a', u_id)

def test_user_remove_invalid_u_id(reset):
    '''
    removing a user who does not exist
    '''
    admin_id, token = register('yousif@gmail.com', 'HelloWorld', 'Yousif', 'Wang')
    u_id, _ = register('josh@gmail.com', 'HelloWorld123', 'Josh', 'Wang')
    with pytest.raises(HTTPError):
        user_remove(token, u_id + admin_id)


def test_user_remove_removed_from_channels(reset):
    '''
    removing a user should remove him from all channels he has joined
    '''
    _, admin_token = register('yousif@gmail.com', 'HelloWorld', 'Yousif', 'Wang')
    u_id, u_token = register('josh@gmail.com', 'HelloWorld123', 'Josh', 'Wang')
    #admin creates a channel
    channel_id = channels_create(admin_token, 'Da channel', is_public=True)
    #joining..
    channel_join(u_token, channel_id)
    #new user is removed
    user_remove(admin_token, u_id)
    #should only contain the admin now
    _, _, all_membs = channel_details(admin_token, channel_id)
    assert len(all_membs) == 1

def test_user_remove_removed_message(reset):
    '''
    A removed user has all the messages he has sent removed
    '''
    _, admin_token = register('yousif@gmail.com', 'HelloWorld', 'Yousif', 'Wang')
    u_id, u_token = register('josh@gmail.com', 'HelloWorld123', 'Josh', 'Wang')
    #admin creates a channel
    channel_id = channels_create(admin_token, 'Da channel', is_public=True)
    #joining..
    channel_join(u_token, channel_id)
    #send a message
    message_send(u_token, channel_id, 'HelloWorld')
    #new user is removed
    user_remove(admin_token, u_id)
    #their message should be removed from the channel
    messages, _, _ = channel_messages(admin_token, channel_id, start=0)
    assert len(messages) == 0

def test_user_remove_own(reset):
    '''
    Invalid request to remove one's ownself
    '''
    admin_info, admin_token = register('yousif@gmail.com', 'HelloWorld', 'Yousif', 'Wang')
    with pytest.raises(HTTPError):
        user_remove(admin_token, admin_info)

# can produce a list of users


def test_users_all(reset):
    '''
    Valid test for users_all
    '''
    j_id, j_token = register("joshwang@gmail.com",
                             "paris in the rain", "Josh", "Wang")
    k_id = register("kenli@gmail.com", "pianoforte", "Ken", "Li")[0]
    i_id = register("ianjacobs@hotmail.com",
                    "ilovetrimesters", "Ian", "Jacobs")[0]
    h_id = register("harrypartridge@yahoo.com.au",
                    "datascience", "Harry", "Partridge")[0]

    everyone = users_all(j_token)['users']
    assert len(everyone) == 4
    assert everyone[0]['u_id'] == j_id
    assert everyone[1]['u_id'] == k_id
    assert everyone[2]['u_id'] == i_id
    assert everyone[3]['u_id'] == h_id


def test_users_all_data_missing(reset):
    '''
    Invalid requesting missing some data
    '''
    register("joshwang@gmail.com", "paris in the rain", "Josh", "Wang")
    register("kenli@gmail.com", "pianoforte", "Ken", "Li")
    with pytest.raises(HTTPError):
        urllib.request.urlopen(urls.USERS_ALL_URL)


def test_search_1(reset):
    '''
    can search a variety of strings sent by different users
    in a multitude of channels of which the auth user is part
    '''
    j_token = register("joshwang@gmail.com",
                       "paris in the rain", "Josh", "Wang")[1]
    k_token = register("kenli@gmail.com", "pianoforte", "Ken", "Li")[1]
    i_token = register("ianjacobs@hotmail.com",
                       "ilovetrimesters", "Ian", "Jacobs")[1]

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
    '''
    Searching for an empty string
    '''
    j_token = register("joshwang@gmail.com",
                       "paris in the rain", "Josh", "Wang")[1]
    ch_id = channels_create(j_token, "new_channel", True)
    message_send(j_token, ch_id, "First message")
    message_send(j_token, ch_id, "Second message")
    assert len(search(j_token, "")["messages"]) == 0

# query string too long


def test_search_query_str_too_long(reset):
    '''
    Invalid request with a long query string
    '''
    j_token = register("joshwang@gmail.com",
                       "paris in the rain", "Josh", "Wang")[1]
    ch_id = channels_create(j_token, "new_channel", True)
    message_send(j_token, ch_id, "First message")
    message_send(j_token, ch_id, "Second message")

    with pytest.raises(HTTPError):
        search(j_token, "i"*1001)

# data missing


def test_search_data_missing(reset):
    '''
    Missing query string in request
    '''
    j_token = register("joshwang@gmail.com",
                       "paris in the rain", "Josh", "Wang")[1]
    ch_id = channels_create(j_token, "new_channel", True)
    message_send(j_token, ch_id, "First message")

    data = urllib.parse.urlencode({
        'token': j_token
    })

    with pytest.raises(HTTPError):
        urllib.request.urlopen(f"{urls.SEARCH_URL}?{data}")

# invalid token tests


def test_userpermission_change_invalid_token(reset):
    '''
    Invalid request with invalid token
    '''
    j_token = register("joshwang@gmail.com",
                       "paris in the rain", "Josh", "Wang")[1]
    k_id = register("kenli@hotmail.com",
                    "asd;fkljas;dfljklas;df", "Ken", "Li")[0]
    with pytest.raises(HTTPError):
        userpermission_change(j_token + 'x', k_id, 1)


def test_userpermission_change_demote_own(reset):
    '''
    Invalid request to demote ones ownself
    '''
    admin_id, admin_token = register('Hola@gmail.com', 'asdasdasd', 'Yousif', 'Khalid')
    with pytest.raises(HTTPError):
        userpermission_change(admin_token, admin_id, 2)

def test_users_all_invalid_token(reset):
    '''
    Invalid request with invalid token
    '''
    j_token = register("joshwang@gmail.com",
                       "paris in the rain", "Josh", "Wang")[1]
    register("kenli@hotmail.com", "asd;fkljas;dfljklas;df", "Ken", "Li")
    with pytest.raises(HTTPError):
        users_all(j_token + 'x')


def test_search_invalid_token(reset):
    '''
    Invalid request with invalid token
    '''
    j_token = register("joshwang@gmail.com",
                       "paris in the rain", "Josh", "Wang")[1]
    ch_id = channels_create(j_token, "new_channel", True)
    message_send(j_token, ch_id, "First message")
    with pytest.raises(HTTPError):
        search(j_token + 'x', 'First')
