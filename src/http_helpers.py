'''
Module contains fixtures used in http tests
'''
import json
import urllib.request
import pytest
import urls

@pytest.fixture
def reset():
    '''
    HTTP request to reset server state
    '''
    request = urllib.request.Request(urls.RESET_URL, method='POST')
    urllib.request.urlopen(request)

def register(email, password, name_first, name_last):
    '''
    HTTP request to register user
    '''
    payload = json.dumps({
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last,
    }).encode()
    request = urllib.request.Request(urls.REGISTER_URL, data=payload, \
        method='POST', headers={'Content-Type':'application/json'})
    reg_details = json.load(urllib.request.urlopen(request))
    return reg_details['u_id'], reg_details['token']

def login(email, password):
    '''
    HTTP request to log user in
    '''
    payload = json.dumps({
        'email': email,
        'password': password,
    }).encode()
    request = urllib.request.Request(urls.LOGIN_URL, data=payload, \
        method='POST', headers={'Content-Type':'application/json'})
    log_details = json.load(urllib.request.urlopen(request))
    return log_details['u_id'], log_details['token']

def logout(token):
    '''
    HTTP request to log out
    '''
    payload = json.dumps({
        'token': token
    }).encode()
    request = urllib.request.Request(urls.LOGOUT_URL, data=payload, \
        method='POST', headers={'Content-Type':'application/json'})
    success = json.load(urllib.request.urlopen(request))

    return success['is_success']


def message_send(token, channel_id, message):
    '''
    HTTP request to send a message
    '''
    data = json.dumps({
        'token': token,
        'channel_id': channel_id,
        'message': message,
    }).encode()
    request = urllib.request.Request(urls.SEND_URL, data=data, \
        method='POST', headers={'Content-Type':'application/json'})
    msg_details = json.load(urllib.request.urlopen(request))
    return msg_details['message_id']

def channels_create(token, name, is_public):
    '''
    HTTP request to create a channel
    '''
    data = json.dumps({
        'token': token,
        'name': name,
        'is_public': is_public,
    }).encode()
    request = urllib.request.Request(urls.CHANNELS_CREATE_URL, data=data, \
        method='POST', headers={'Content-Type':'application/json'})
    channel_info = json.load(urllib.request.urlopen(request))
    return channel_info['channel_id']

def channel_messages(token, channel_id, start):
    '''
    HTTP request to get channel messages
    '''
    data = json.dumps({
        'token': token,
        'channel_id': channel_id,
        'start': start,
    }).encode()
    request = urllib.request.Request(urls.MESSAGES_URL, data=data, \
        method='GET', headers={'Content-Type':'application/json'})
    messages = json.load(urllib.request.urlopen(request))
    return messages['messages'], messages['start'], messages['end']

def channel_join(token, channel_id):
    '''
    HTTP request to join a channel
    '''
    data = json.dumps({
        'token': token,
        'channel_id': channel_id
    }).encode()
    request = urllib.request.Request(urls.JOIN_URL, data=data, \
        method='POST', headers={'Content-Type':'application/json'})
    urllib.request.urlopen(request)

def channel_leave(token, channel_id):
    '''
    HTTP request to leave a channel
    '''
    data = json.dumps({
        'token': token,
        'channel_id': channel_id
    }).encode()
    request = urllib.request.Request(urls.LEAVE_URL, data=data, \
        method='POST', headers={'Content-Type':'application/json'})
    urllib.request.urlopen(request)

def channel_addowner(token, channel_id, u_id):
    '''
    HTTP request to add owner
    '''
    data = json.dumps({
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id
    }).encode()
    request = urllib.request.Request(urls.ADDOWNER_URL, data=data, \
        method='POST', headers={'Content-Type':'application/json'})
    urllib.request.urlopen(request)

def channel_removeowner(token, channel_id, u_id):
    '''
    HTTP request to remove owner
    '''
    data = json.dumps({
        'token': token,
        'channel_id': channel_id,
        'u_id': u_id
    }).encode()
    request = urllib.request.Request(urls.REMOVEOWNER_URL, data=data, \
        method='POST', headers={'Content-Type':'application/json'})
    urllib.request.urlopen(request)

def message_remove(token, message_id):
    '''
    HTTP request to remove a message
    '''
    data = json.dumps({
        'token': token,
        'message_id': message_id
    }).encode()
    request = urllib.request.Request(urls.MESSAGE_REMOVE_URL, data=data, \
        method='DELETE', headers={'Content-Type':'application/json'})
    urllib.request.urlopen(request)

def channels_list(token):
    '''
    HTTP request to get the channels the user is part of
    '''
    data = json.dumps({
        'token': token
    }).encode()
    request = urllib.request.Request(urls.CHANNELS_LIST_URL, data=data, \
        method='GET', headers={'Content-Type':'application/json'})
    channel_list = json.load(urllib.request.urlopen(request))
    return channel_list['channels']

def channels_listall(token):
    '''
    HTTP request to get all the channels that exist in slackr
    '''
    data = json.dumps({
        'token': token
    }).encode()
    request = urllib.request.Request(urls.CHANNELS_LISTALL_URL, data=data, \
        method='GET', headers={'Content-Type':'application/json'})
    all_list = json.load(urllib.request.urlopen(request))
    return all_list['channels']