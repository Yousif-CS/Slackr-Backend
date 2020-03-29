import json
import urllib.request
from urllib.error import HTTPError
import pytest

import urls
from http_helpers import reset, register, login, logout, channels_list, \
    channels_create, channels_listall


# start testing on channels_create
def test_channels_create_ok(reset):
    '''
    Testing creating a channel with correct inputs functions correctly
    '''
    a_id, a_token = register('admin@gmail.com', 'pass123456', 'Alan', 'Brown')
    channels_create(a_token, 'test_public', True)
    payload = channels_list(a_token)[0]
    # asserting
    assert payload['channel_id'] == 1
    assert payload['name'] == 'test_public'
    logout(a_token)

def test_channels_create_bad():
    '''
    Testing invalid inputs (e.g. name too long) will be picked up and thrown error
    '''
    a_id, a_token = login('admin@gmail.com', 'pass123456')
    with pytest.raises(HTTPError):
        channels_create(a_token, 225, True)

def test_channels_create_invalid_token():
    '''
    Testing valid token when attempting to create channel
    '''
    a_id, a_token = login('admin@gmail.com', 'pass123456')
    with pytest.raises(HTTPError):
        channels_create(a_token + 'bad', 'test_name', True)


def test_channels_list_empty(reset):
    '''
    no channels created yet
    '''
    a_id, a_token = register('admin@gmail.com', 'pass123456', 'Alan', 'Brown')
    payload = channels_list(a_token)
    # check the list is empty
    assert payload == []
    logout(a_token)

def test_channels_list_ok():
    '''
    single channel created by admin
    '''
    a_id, a_token = login('admin@gmail.com', 'pass123456')
    channels_create(a_token, 'test_public', True)
    payload = channels_list(a_token)
    # check now channel list includes the new channel
    assert payload == [{
        'channel_id': 1,
        'name': 'test_public',
    }]
    logout(a_token)

def test_channels_list_multiple():
    '''
    multiple channels (public and private)
    '''
    k_id, k_token = register('ken@gmail.com', 'kenisaperson', 'Ken', 'Li')
    a_id, a_token = login('admin@gmail.com', 'pass123456')
    # both admin and ken create a channel each
    channels_create(a_token, 'test_priv', False)
    channels_create(k_token, 'ken_channel', True)
    # checking that all channels are added
    assert channels_list(a_token) == [
        {
            'channel_id': 1,
            'name': 'test_public',
        },
        {
            'channel_id': 2,
            'name': 'test_priv',
        }]
    assert channels_list(k_token) == [{
        'channel_id': 3,
        'name': 'ken_channel',
    }]
    logout(k_id)
    logout(a_id)

def test_channels_list_invalid_token():
    '''
    Testing invalid token
    '''
    a_id, a_token = login('admin@gmail.com', 'pass123456')
    # chuck in invalid token
    with pytest.raises(HTTPError):
        channels_list(a_token + 'invalid')

def test_channels_listall_ok():
    '''
    Testing listing all channels when there are multiple
    '''
    a_id, a_token = login('admin@gmail.com', 'pass123456')
    k_id, k_token = login('ken@gmail.com', 'kenisaperson')
    # assert both users get the same list when calling listall
    assert channels_listall(a_token) == channels_listall(k_token) == [
        {
            'channel_id': 1,
            'name': 'test_public',
        },
        {
            'channel_id': 2,
            'name': 'test_priv',
        },
        {
            'channel_id': 3,
            'name': 'ken_channel',
        }]
    logout(a_token)
    logout(k_token)
  
def test_channels_listall_empty(reset):
    '''
    Testing return of empty payload when no channels exist
    '''
    a_id, a_token = register('admin@gmail.com', 'pass123456', 'Alan', 'Brown')
 
    assert channels_listall(a_token) == []
    logout(a_token)

def test_channels_listall_invalid_token():
    '''
    Testing invalid token
    '''
    a_id, a_token = login('admin@gmail.com', 'pass123456')
    # chuck in invalid token
    with pytest.raises(HTTPError):
        channels_listall(a_token + 'invalid')


