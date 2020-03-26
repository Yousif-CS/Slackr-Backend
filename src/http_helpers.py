'''
Module contains fixtures used in http tests
'''

import requests

import urls

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
    return (reg_details['u_id'], reg_details['token'])

def login(email, password):
    '''
    HTTP request to log user in
    '''
    data = {
        'email': email,
        'password': password,
    }
    log_details = requests.post(urls.LOGIN_URL, data=data).json()
    return (log_details['u_id'], log_details['token'])

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
