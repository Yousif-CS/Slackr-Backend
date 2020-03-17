from time import time
from server import get_store, get_tokens
from auth import verify_token
from error import InputError, AccessError

# TODO: check structure for TOKENS dictionary

def message_send(token, channel_id, message):
    '''
    input: valid token, channel_id to send message into, actual message string
    output:
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
    # assigning new message_id
    if len(data['Channels'][channel_id]['message']) == 0:
        new_msg_id = 0
    else:
        new_msg_id = max(data['Channels'][channel_id]['message']) + 1
    # sending the actual message:
    # 1. append to list of message id's
    data['Channels'][channel_id]['message'].append(new_msg_id)
    # 2. new dictionary in data['Messages']
    data['Messages'].append({
        'message_id': new_msg_id,
        'message': message,
        'u_id': u_id,
        'time_created': time(),
        'is_pinned': False,
        'reacts': {}
    })


def message_sendlater(token, channel_id, message, time_sent):
    pass

def message_pin(token, message_id):
    pass

def message_unpin(token, message_id):
    pass

def message_remove(token, message_id):
    pass

