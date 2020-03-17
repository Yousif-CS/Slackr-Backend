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

def message_pin(token, message_id):
    '''
    input: token, message_id
    output: {}
    Given message within a channel, mark it as 'pinned'
    '''
    # verify the user
    if verify_token(token) is False:
        raise InputError(description='Invalid token')

    # get database
    data = get_store()
    # getting id of the user
    u_id = get_tokens()[token]
    # check for valid message ID by looking for that ID in every channel the user is part of
    for joined_channel_id in data['Users'][u_id]['channels']:
        for msg_ids in data['Channels'][joined_channel_id]['messages']:
            if message_id == msg_ids:
                matching_channel_id = joined_channel_id
                valid_message_id = True
    if not valid_message_id:
        raise InputError(description='You have provided an invalid message ID')
    # checking user is admin in the channel containing message_id
    if u_id not in data['Channels'][matching_channel_id]['owner_members']:
        raise InputError(description='You are not an admin of the channel')
    # checking if message is already pinned
    for msgs in range(len(data['Messages'])):
        if message_id == data['Messages'][msgs]['message_id']:
            if data['Messages'][msgs]['is_pinned']:
                raise InputError(description='Message already pinned')

    # AccessError !!!

    '''
    Proper ordering of message_pin validity check:
    search for message_id in all the channels first
        if message_id in some_channel:
            if some_channel_id not in u_id.channels:
                raise AccessError (not a member of channel where message is in)
            else if u_id not in some_channel.owner_members:
                raise InputError (not admin)
            else if message_id.is_pinned:
                raise InputError (already pinned)
            else: valid = True
        if not valid: 
            raise InputError (not valid message)
    '''
    return {}

def message_unpin(token, message_id):
    pass

def message_remove(token, message_id):
    pass
