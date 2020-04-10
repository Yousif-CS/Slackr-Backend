'''
Module contains fixtures used in http tests
'''
#pylint: disable=trailing-whitespace

import json
import urllib.request
import urllib.parse
import pytest
import urls

BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture
def reset():
    '''
    HTTP request to reset server state
    '''
    request = urllib.request.Request(urls.RESET_URL, method='POST')
    urllib.request.urlopen(request)


# --------------------------auth--------------------------


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
    request = urllib.request.Request(urls.REGISTER_URL, data=payload,
                                     method='POST', headers={'Content-Type': 'application/json'})
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
    request = urllib.request.Request(urls.LOGIN_URL, data=payload,
                                     method='POST', headers={'Content-Type': 'application/json'})
    log_details = json.load(urllib.request.urlopen(request))
    return log_details['u_id'], log_details['token']


def logout(token):
    '''
    HTTP request to log out
    '''
    payload = json.dumps({
        'token': token
    }).encode()
    request = urllib.request.Request(urls.LOGOUT_URL, data=payload,
                                     method='POST', headers={'Content-Type': 'application/json'})
    success = json.load(urllib.request.urlopen(request))

    return success['is_success']


# --------------------------message--------------------------


def message_send(token, channel_id, message):
    '''
    HTTP request to send a message
    '''
    data = json.dumps({
        'token': token,
        'channel_id': channel_id,
        'message': message,
    }).encode()
    request = urllib.request.Request(urls.SEND_URL, data=data,
                                     method='POST', headers={'Content-Type': 'application/json'})
    msg_details = json.load(urllib.request.urlopen(request))
    return msg_details['message_id']


def message_sendlater(token, channel_id, message, time_sent):
    '''
    HTTP request to send message at specified time
    '''
    data = json.dumps({
        'token': token,
        'channel_id': channel_id,
        'message': message,
        'time_sent': time_sent,
    }).encode()
    request = urllib.request.Request(urls.SENDLATER_URL, data=data, \
        method='POST', headers={'Content-Type':'application/json'})
    msg_details = json.load(urllib.request.urlopen(request))
    return msg_details['message_id']


def message_remove(token, message_id):
    '''
    HTTP request to remove a message
    '''
    data = json.dumps({
        'token': token,
        'message_id': message_id
    }).encode()
    request = urllib.request.Request(urls.MESSAGE_REMOVE_URL, data=data,
                                     method='DELETE', headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(request)


def message_edit(token, message_id, message):
    '''
    HTTP request to edit a message
    '''
    data = json.dumps({
        'token': token,
        'message_id': message_id,
        'message': message
    }).encode()

    request = urllib.request.Request(urls.EDIT_URL, data=data,
                                     method='PUT', headers={'Content-Type': 'application/json'})

    urllib.request.urlopen(request)

def message_react(token, message_id, react_id):
    '''
    HTTP request to react to a given message
    '''
    data = json.dumps({
        'token': token,
        'message_id': message_id,
        'react_id': react_id,
    }).encode()
    request = urllib.request.Request(urls.REACT_URL, data=data,
                                     method='POST', headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(request)

def message_unreact(token, message_id, react_id):
    '''
    HTTP request to unreact to a given message
    '''
    data = json.dumps({
        'token': token,
        'message_id': message_id,
        'react_id': react_id,
    }).encode()
    request = urllib.request.Request(urls.UNREACT_URL, data=data,
                                     method='POST', headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(request)

def message_pin(token, message_id):
    '''
    HTTP request to pin a message
    '''
    data = json.dumps({
        'token': token,
        'message_id': message_id,
    }).encode()
    request = urllib.request.Request(urls.PIN_URL, data=data,
                                     method='POST', headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(request)

def message_unpin(token, message_id):
    '''
    HTTP request to unpin a message
    '''
    data = json.dumps({
        'token': token,
        'message_id': message_id,
    }).encode()
    request = urllib.request.Request(urls.UNPIN_URL, data=data,
                                     method='POST', headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(request)

# --------------------------channels--------------------------


def channels_create(token, name, is_public):
    '''
    HTTP request to create a channel
    '''
    data = json.dumps({
        'token': token,
        'name': name,
        'is_public': is_public,
    }).encode()
    request = urllib.request.Request(urls.CHANNELS_CREATE_URL, data=data,
                                     method='POST', headers={'Content-Type': 'application/json'})
    channel_info = json.load(urllib.request.urlopen(request))
    return channel_info['channel_id']


def channels_list(token):
    '''
    HTTP request to get the channels the user is part of
    '''
    query = urllib.parse.urlencode({
        'token': token
    })
    channel_list = json.load(urllib.request.urlopen(
        f"{BASE_URL}/channels/list?{query}"))
    return channel_list['channels']


def channels_listall(token):
    '''
    HTTP request to get all the channels that exist in slackr
    '''
    query = urllib.parse.urlencode({
        'token': token
    })

    all_list = json.load(urllib.request.urlopen(f"{BASE_URL}/channels/listall?{query}"))
    return all_list['channels']


# --------------------------channel--------------------------


def channel_invite(token, channel_id, user_id): 
    '''
    HTTP request to invite user to a channel
    '''
    data = json.dumps({
        'token': token,
        'channel_id': channel_id,
        'u_id' : user_id
    }).encode()

    request = urllib.request.Request(urls.INVITE_URL, data=data, method='POST', headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(request)


def channel_details(token, channel_id):
    ''' 
    HTTP request to gather details of a channel user is part of
    '''
    query = urllib.parse.urlencode({
        'token': token,
        'channel_id': channel_id
    })
    details = json.load(urllib.request.urlopen(
        f"{urls.CHANNEL_DETAILS_URL}?{query}"))
    return details['name'], details['owner_members'], details['all_members']
 


def channel_messages(token, channel_id, start):
    '''
    HTTP request to get channel messages
    '''
    query = urllib.parse.urlencode({
        'token': token,
        'channel_id': channel_id,
        'start': start,
    })
    messages = json.load(urllib.request.urlopen(
        f"{urls.MESSAGES_URL}?{query}"))
    return messages['messages'], messages['start'], messages['end']


def channel_join(token, channel_id):
    '''
    HTTP request to join a channel
    '''
    data = json.dumps({
        'token': token,
        'channel_id': channel_id
    }).encode()
    request = urllib.request.Request(urls.JOIN_URL, data=data,
                                     method='POST', headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(request)


def channel_leave(token, channel_id):
    '''
    HTTP request to leave a channel
    '''
    data = json.dumps({
        'token': token,
        'channel_id': channel_id
    }).encode()
    request = urllib.request.Request(urls.LEAVE_URL, data=data,
                                     method='POST', headers={'Content-Type': 'application/json'})
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
    request = urllib.request.Request(urls.ADDOWNER_URL, data=data,
                                     method='POST', headers={'Content-Type': 'application/json'})
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
    request = urllib.request.Request(urls.REMOVEOWNER_URL, data=data,
                                     method='POST', headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(request)


# --------------------------standup--------------------------


def standup_start(token, channel_id, length):
    '''
    HTTP request to start a standup
    '''
    data = json.dumps({
        'token': token,
        'channel_id': channel_id,
        'length': length
    }).encode()

    request = urllib.request.Request(urls.STANDUP_START_URL, data=data,
                                     method='POST', headers={'Content-Type': 'application/json'})
    payload = json.load(urllib.request.urlopen(request))
    return payload['time_finish']


def standup_active(token, channel_id):
    '''
    HTTP request to check a standup is active
    '''
    query = urllib.parse.urlencode({
        'token': token,
        'channel_id': channel_id,
    })
    payload = json.load(urllib.request.urlopen(
        f"{urls.STANDUP_ACTIVE_URL}?{query}"))
    return payload['is_active'], payload['time_finish']


def standup_send(token, channel_id, message):
    '''
    HTTP request to start a standup
    '''
    data = json.dumps({
        'token': token,
        'channel_id': channel_id,
        'message': message
    }).encode()

    request = urllib.request.Request(urls.STANDUP_SEND_URL, data=data,
                                     method='POST', headers={'Content-Type': 'application/json'})
    urllib.request.urlopen(request)


# --------------------------user--------------------------


def user_profile(token, u_id):
    '''
    HTTP request to retrieve infomration about another user
    '''
    query = urllib.parse.urlencode({
        'token': token,
        'u_id': u_id
    })
    payload = json.load(urllib.request.urlopen(f"{urls.PROFILE_URL}?{query}"))

    return payload['user']


def user_profile_setname(token, name_first, name_last):
    '''
    HTTP request to set the name of the authorised user
    '''
    data = json.dumps({
        'token': token,
        'name_first': name_first,
        'name_last': name_last
    }).encode()
    # creating the request - "preparing"
    request = urllib.request.Request(urls.SETNAME_URL, data=data,
                                     method='PUT', headers={'Content-Type': 'application/json'})

    # actually sends the request
    urllib.request.urlopen(request)


def user_profile_setemail(token, email):
    '''
    HTTP request to set the email of the authorised user
    '''

    data = json.dumps({
        'token': token,
        'email': email
    }).encode()
    request = urllib.request.Request(urls.SETEMAIL_URL, data=data,
                                     method='PUT', headers={'Content-Type': 'application/json'})

    urllib.request.urlopen(request)


def user_profile_sethandle(token, handle_str):
    '''
    HTTP request to set the handle of the authorised user
    '''
    data = json.dumps({
        'token': token,
        'handle_str': handle_str
    }).encode()

    request = urllib.request.Request(urls.SETHANDLE_URL, data=data,
                                     method='PUT', headers={"Content-Type": "application/json"})

    urllib.request.urlopen(request)


# --------------------------other--------------------------


def userpermission_change(token, u_id, permission_id):
    '''
    HTTP request to change user permissions
    '''
    data = json.dumps({
        'token': token,
        'u_id': u_id,
        'permission_id': permission_id
    }).encode()

    request = urllib.request.Request(urls.PERMISSION_CHANGE_URL, data=data,
                                     method='POST', headers={'Content-Type': 'application/json'})

    urllib.request.urlopen(request)

def user_remove(token, u_id):
    '''
    HTTP request to change user permissions
    '''
    data = json.dumps({
        'token': token,
        'u_id': u_id
    }).encode()

    request = urllib.request.Request(urls.USER_REMOVE_URL, data=data,
                                     method='DELETE', headers={'Content-Type': 'application/json'})

    urllib.request.urlopen(request)

def users_all(token):
    '''
    HTTP request to access the profiles of all users
    '''
    query = urllib.parse.urlencode({
        'token': token
    })

    payload = json.load(urllib.request.urlopen(
        f"{BASE_URL}/users/all?{query}"))

    return payload


def search(token, query_str):
    '''
    HTTP request to search messages for the query_str
    '''
    query = urllib.parse.urlencode({
        'token': token,
        'query_str': query_str
    })

    payload = json.load(urllib.request.urlopen(f"{BASE_URL}/search?{query}"))
    return payload
