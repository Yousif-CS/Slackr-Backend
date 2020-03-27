'''
Module contains fixtures used in http tests
'''

import requests
import pytest
import urls

@pytest.fixture
def reset():
    '''
    HTTP request to reset server state
    '''
    requests.post(urls.RESET_URL)

def register(email, password, name_first, name_last):
    '''
    HTTP request to register user
    '''
    data = {
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last,
    }
    reg_details = requests.post(urls.REGISTER_URL, data=data).json()
    return reg_details['u_id'], reg_details['token']

def login(email, password):
    '''
    HTTP request to log user in
    '''
    data = {
        'email': email,
        'password': password,
    }
    log_details = requests.post(urls.LOGIN_URL, data=data).json()
    return log_details['u_id'], log_details['token']

def message_send(token, channel_id, message):
    '''
    HTTP request to send a message
    '''
    data = {
        'token': token,
        'channel_id': channel_id,
        'message': message,
    }
    msg_details = requests.post(urls.SEND_URL, data=data).json()
    return msg_details['message_id']

def channels_create(token, name, is_public):
    '''
    HTTP request to create a channel
    '''
    data = {
        'token': token,
        'name': name,
        'is_public': is_public,
    }
    channel_info = requests.post(urls.CHANNELS_CREATE_URL, data=data).json()
    return channel_info['channel_id']

def channel_messages(token, channel_id, start):
    '''
    HTTP request to get channel messages
    '''
    data = {
        'token': token,
        'channel_id': channel_id,
        'start': start,
    }
    messages = requests.post(urls.MESSAGES_URL, data=data).json()
    return messages['messages'], messages['start'], messages['end']

def channels_list(token):
    '''
    HTTP request to get the channels the user is part of
    '''
    data = {
        'token': token
    }
    channel_list = requests.get(urls.CHANNELS_LIST_URL, data=data).json()
    return channel_list['channels']
