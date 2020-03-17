from time import time
from server import get_store, get_tokens
from auth import verify_token
from error import InputError, AccessError

# TODO: check structure for TOKENS dictionary
# TODO: import sched? need pip install

def message_send(token, channel_id, message):
    '''
    input: valid token, channel_id to send message into, actual message string
    output: a globally unique message_id in dictionary
    '''
    # verify the user
    if verify_token(token) is False:
        raise InputError(description='Invalid token')

    # get database
    data = get_store()
    # getting id of the user
    u_id = get_tokens()[token]

    # checking message string is valid
    if not isinstance(message, str) or len(message) > 1000 or len(message) == 0:
        raise InputError(description='Invalid message')
    # checking channel_id is valid (user is part of)
    if channel_id not in data['Users'][u_id]['channels']:
        raise AccessError(description='You do not have access to send message in this channel')
    # assigning new message_id MUST BE GLOBALLY UNIQUE!
    # starting from index 0
    if len(data['Messages']) == 0:
        new_msg_id = 0
    else:
        id_list = []
        for i in range(len(data['Messages'])):
            id_list.append(data['Messages'][i]['message_id'])
        new_msg_id = max(id_list) + 1
    # sending the actual message:
    # 1. append to list of message id's
    data['Channels'][channel_id]['message'].append(new_msg_id)
    # 2. new dictionary in data['Messages']
    data['Messages'].append({
        'message_id': new_msg_id,
        'channel_id': channel_id,
        'message': message,
        'u_id': u_id,
        'time_created': time(),
        'is_pinned': False,
        'reacts': {}
    })

    return {'message_id': new_msg_id}


def message_sendlater(token, channel_id, message, time_sent):
    '''
    input: valid token, channel_id, message and time in the future
    output: {message_id}; 
    Sends message from user to channel (specified by id) at specific time, automatically
    '''

# TODO: how to know 
def message_pin(token, message_id):
    '''
    input: token, message_id
    output: {}
    Given message within a channel, mark it as 'pinned' 
    '''
    return {}

def message_unpin(token, message_id):
    pass

def message_remove(token, message_id):
    pass

