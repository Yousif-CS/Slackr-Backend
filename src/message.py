import sched
from time import time, sleep
from server import get_store, get_tokens
from auth import verify_token
from error import InputError, AccessError

# TODO: check structure for TOKENS dictionary
# TODO: import sched? need pip install

MAX_MSG_LEN = 1000

def message_send(token, channel_id, message):
    '''
    input: valid token, channel_id to send message into, actual message string
    output: a globally unique message_id in dictionary
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    # get database
    data = get_store()
    # getting id of the user
    u_id = get_tokens()[token]

    # checking message string is valid
    if not isinstance(message, str) or len(message) > MAX_MSG_LEN or len(message) == 0:
        raise InputError(description='Invalid message')

    # checking channel_id is valid (user is part of)
    if channel_id not in data['Users'][u_id]['channels']:
        raise AccessError(description='You do not have access to send message in this channel')
    # assigning new message_id MUST BE GLOBALLY UNIQUE!
    # starting from index 0
    if len(data['Messages']) == 0:
        new_msg_id = 0
    else:
        id_list = [msg['message_id'] for msg in data['Messages']]
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
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    # get database
    data = get_store()
    # getting id of the user
    u_id = get_tokens()[token]

    # checking message string is valid
    if not isinstance(message, str) or len(message) > MAX_MSG_LEN or len(message) == 0:
        raise InputError(description='Invalid message')

    # checking channel_id is valid (user is part of)
    if channel_id not in data['Users'][u_id]['channels']:
        raise AccessError(description='You do not have access to send message in this channel')

    # checking time_sent is valid (it is a time in the future)
    if time_sent <= time():
        raise InputError(description='Scheduled send time is invalid')

    # assigning new message_id MUST BE GLOBALLY UNIQUE!
    # starting from index 0
    if len(data['Messages']) == 0:
        new_msg_id = 0
    else:
        id_list = [msg['message_id'] for msg in data['Messages']]
        new_msg_id = max(id_list) + 1
    # the action to be completed at time time_sent
    def auto_send_message():
        data['Channels'][channel_id]['message'].append(new_msg_id)
        data['Messages'].append({
            'message_id': new_msg_id,
            'channel_id': channel_id,
            'message': message,
            'u_id': u_id,
            'time_created': time_sent,
            'is_pinned': False,
            'reacts': {}
        })
    # setting up scheduler object
    s = sched.scheduler(time, sleep)
    # setting auto_send_message to be called at 'time_sent'
    s.enterabs(time_sent, 0, auto_send_message)
    s.run()

    return {'message_id': new_msg_id}

# TODO: how to know 
def message_pin(token, message_id):
    '''
    input: token, message_id
    output: {}
    Given message within a channel, mark it as 'pinned'
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    # get database
    data = get_store()
    # getting id of the user
    u_id = get_tokens()[token]

    # check for valid message ID by looking for that ID in every channel the user is part of
    valid_message_id = False
    for joined_channel_id in data['Users'][u_id]['channels']:
        for msg_ids in data['Channels'][joined_channel_id]['messages']:
            if message_id == msg_ids:
                matching_channel_id = joined_channel_id
                valid_message_id = True

    # check for AccessError or InputError: does message_id exist at all?
    if not valid_message_id:
        for each_dict in data['Messages']:
            if message_id == each_dict['message_id']:
                raise AccessError(description='Not member of the channel which the message is in')
        raise InputError(description='You have provided an invalid message ID')

    # checking user is admin in the channel containing message_id
    if u_id not in data['Channels'][matching_channel_id]['owner_members']:
        raise InputError(description='You are not an admin of the channel')

    # checking if message is already pinned
    for msgs in data['Messages']:
        if message_id == data['Messages'][msgs]['message_id']:
            if data['Messages'][msgs]['is_pinned']:
                raise InputError(description='Message already pinned')
            # pinning the message if it's not yet pinned
            data['Messages'][msgs]['is_pinned'] = True
    return {}

def message_unpin(token, message_id):
    '''
    input: token, message_id
    output: {}
    Given message within a channel, remove its pinned status and unpin it
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    # get database
    data = get_store()
    # getting id of the user
    u_id = get_tokens()[token]

    # check for valid message ID by looking for that ID in every channel the user is part of
    valid_message_id = False
    for joined_channel_id in data['Users'][u_id]['channels']:
        for msg_ids in data['Channels'][joined_channel_id]['messages']:
            if message_id == msg_ids:
                matching_channel_id = joined_channel_id
                valid_message_id = True

    # check for AccessError or InputError: does message_id exist at all?
    if not valid_message_id:
        for each_dict in data['Messages']:
            if message_id == each_dict['message_id']:
                raise AccessError(description='Not member of the channel which the message is in')
        raise InputError(description='You have provided an invalid message ID')

    # checking user is admin in the channel containing message_id
    if u_id not in data['Channels'][matching_channel_id]['owner_members']:
        raise InputError(description='You are not an admin of the channel')

    # checking if message is already unpinned
    for msgs in data['Messages']:
        if message_id == data['Messages'][msgs]['message_id']:
            if not data['Messages'][msgs]['is_pinned']:
                raise InputError(description='Message already unpinned')
            # unpinning the message if it's pinned
            data['Messages'][msgs]['is_pinned'] = False
    return {}

def message_remove(token, message_id):
    '''
    input: valid token, message_id of message to be removed
    output: {}; just removes message from the channel
    errors: InputError when message no longer exists (i.e. message_id not exist)
    AccessError: none of: 
        message with message_id sent by user making the request
        authorised user is admin or owner of this channel or slackr
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    # get database
    data = get_store()
    # getting id of the user
    u_id = get_tokens()[token]
    
    # checking if the message with message_id exists
    id_list = [msg['message_id'] for msg in data['Messages']]
    if message_id not in id_list:
        raise InputError(description='Invalid message ID')

    # given message_id does exist, check for AccessError:
    msg_pos = id_list.index(message_id)
    is_user_delete_own = data['Messages'][msg_pos]['u_id'] == u_id
    matching_channel_id = data['Messages'][msg_pos]['channel_id']
    is_user_owner = u_id in data['Channels'][matching_channel_id]['owner_members']
    is_user_slackr_owner = u_id in data['Slack_owners']

    if not (is_user_delete_own or is_user_owner or is_user_slackr_owner):
        raise AccessError(description='You do not have access to delete this message')

    # passed above checks: delete actual message 
    # 1. delete from message_id list in Channels info
    data['Channels'][matching_channel_id]['messages'].remove(message_id)
    # 2. delete message dictionary from Messages list
    data['Messages'].remove(msg_pos)

    return {}
