'''
Using urllib module to test channels functions
'''
from urllib.error import HTTPError #pylint: disable=missing-module-docstring
import pytest #pylint: disable=import-error
from http_helpers import reset, register, login, logout, channels_list, \
    channels_create, channels_listall #pylint: disable=unused-import


# start testing on channels_create
def test_channels_create_ok(reset): #pylint: disable=unused-argument,redefined-outer-name
    '''
    Testing creating a channel with correct inputs functions correctly
    '''
    a_token = register('admin@gmail.com', 'pass123456', 'Alan', 'Brown')[1]
    channel_id = channels_create(a_token, 'test_public', True)
    payload = channels_list(a_token)
    # asserting
    assert channel_id == 1
    assert len(payload) == 1
    assert payload[0]['channel_id'] == 1
    assert payload[0]['name'] == 'test_public'
    logout(a_token)


def test_channels_create_bad():
    '''
    Testing invalid inputs (e.g. name too long) will be picked up and thrown error
    '''
    a_token = login('admin@gmail.com', 'pass123456')[1]
    with pytest.raises(HTTPError):
        channels_create(a_token, 225, True)

def test_channels_create_invalid_token():
    '''
    Testing valid token when attempting to create channel
    '''
    a_token = login('admin@gmail.com', 'pass123456')[1]
    with pytest.raises(HTTPError):
        channels_create(a_token + 'bad', 'test_name', True)


def test_channels_list_empty(reset): #pylint: disable=unused-argument,redefined-outer-name
    '''
    no channels created yet
    '''
    a_token = register('admin@gmail.com', 'pass123456', 'Alan', 'Brown')[1]
    payload = channels_list(a_token)
    # check the list is empty
    assert payload == []
    logout(a_token)

def test_channels_list_ok():
    '''
    single channel created by admin
    '''
    a_token = login('admin@gmail.com', 'pass123456')[1]
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
    k_token = register('ken@gmail.com', 'kenisaperson', 'Ken', 'Li')[1]
    a_token = login('admin@gmail.com', 'pass123456')[1]
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
    logout(k_token)
    logout(a_token)

def test_channels_list_invalid_token():
    '''
    Testing invalid token
    '''
    a_token = login('admin@gmail.com', 'pass123456')[1]
    # chuck in invalid token
    with pytest.raises(HTTPError):
        channels_list(a_token + 'invalid')

def test_channels_listall_ok():
    '''
    Testing listing all channels when there are multiple
    '''
    a_token = login('admin@gmail.com', 'pass123456')[1]
    k_token = login('ken@gmail.com', 'kenisaperson')[1]
    # assert both users get the same list when calling listall
    payload = channels_listall(a_token)
    payload2 = channels_listall(k_token)
    assert payload == payload2 == [
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


def test_channels_listall_empty(reset): #pylint: disable=unused-argument,redefined-outer-name
    '''
    Testing return of empty payload when no channels exist
    '''
    a_token = register('admin@gmail.com', 'pass123456', 'Alan', 'Brown')[1]

    assert channels_listall(a_token) == []
    logout(a_token)


def test_channels_listall_invalid_token():
    '''
    Testing invalid token
    '''
    a_token = login('admin@gmail.com', 'pass123456')[1]
    # chuck in invalid token
    with pytest.raises(HTTPError):
        channels_listall(a_token + 'invalid')
