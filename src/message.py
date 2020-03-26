import sched
from time import time, sleep
from auth import verify_token
from server import get_store, get_tokens
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
    data['Channels'][channel_id]['messages'].append(new_msg_id)
    # 2. new dictionary in data['Messages']
    data['Messages'].append({
        'message_id': new_msg_id,
        'channel_id': channel_id,
        'message': message,
        'u_id': u_id,
        'time_created': time(),
        'is_pinned': False,
        'reacts': []
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
            'reacts': []
        })
    # setting up scheduler object
    s = sched.scheduler(time, sleep)
    # setting auto_send_message to be called at 'time_sent'
    s.enterabs(time_sent, 0, auto_send_message)
    s.run()

    return {'message_id': new_msg_id}

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

    # checking for InputError and AccessError
    msg_ids = [msg['message_id'] for msg in data['Messages']]
    if message_id not in msg_ids:
        raise InputError(description='Invalid message ID')
    for msg in data['Messages']:
        # locate the message dictionary in data['Messages']
        if msg['message_id'] == message_id:
            # not part of channel where message_id is in
            if msg['channel_id'] not in data['Users']['channels']:
                raise AccessError(description='You are not part of the channel the message is in')
            # neither admin of channel nor slackr owner
            elif u_id not in data['Channels'][msg['channel_id']]['owner_members']:
                if u_id not in data['Slack_owners']:
                    raise AccessError(description='You are not admin of channel')
            # message already pinned
            elif msg['is_pinned'] is True:
                raise InputError(description='Message already pinned')
            # pinning the message
            else:
                msg['is_pinned'] = True
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

    # checking for InputError and AccessError
    msg_ids = [msg['message_id'] for msg in data['Messages']]
    if message_id not in msg_ids:
        raise InputError(description='Invalid message ID')
    for msg in data['Messages']:
        # locate the message dictionary in data['Messages']
        if msg['message_id'] == message_id:
            # not part of channel where message_id is in
            if msg['channel_id'] not in data['Users']['channels']:
                raise AccessError(description='You are not part of the channel the message is in')
            # neither admin of channel nor slackr owner
            elif u_id not in data['Channels'][msg['channel_id']]['owner_members']:
                if u_id not in data['Slack_owners']:
                    raise AccessError(description='You are not admin of channel')
            # message already pinned
            elif msg['is_pinned'] is False:
                raise InputError(description='Message already unpinned')
            # unpinning the message
            else:
                msg['is_pinned'] = False
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


def has_message_edit_permission(auth_u_id, message_id):
    data = get_store()

    # check if auth user is a slackr owner
    if auth_u_id in data["Slack_owners"]:
        return True

    # check if auth user wrote the message
    for msg_dict in data["Messages"]:
        if msg_dict["u_id"] == auth_u_id:
            return True    

    # check if auth user is owner of channel which contains the message
    for ch_dict in data["Channels"].values():
        if message_id in ch_dict["messages"]:
            if auth_u_id in ch_dict["owner_members"]:
                return True
            else:
                return False

def message_edit(token, message_id, message):
    '''
    Given a message, update it's text with new text. If the new message is an empty string, the message is deleted.
    Empty message string: delete message.
    AccessError if request is not made by: authorised user OR (admin or owner) of (channel or slacker).
    '''

    # verify the validity of the token
    if verify_token(token) is False:
        raise AccessError(description="Invalid token")

    # check that the request is being made by a user with the correct permissions
    auth_u_id = get_tokens()[token]
    data = get_store()

    if has_message_edit_permission(auth_u_id, message_id) is False:
        raise AccessError(description="User with this u_id does not have permission to edit this message")

    # delete the message if the message string is empty,
    # otherwise modify the message accordingly in both the "Channels" and "Messages" sub-dictionaries
    if message == "":
        message_remove(token, message_id)
    else:
        for msg_dict in data["Messages"]:
            if msg_dict["message_id"] == message_id:
                msg_dict["message"] = message
                break


# helper function to check if user has active react on a given react id
def has_user_reacted_react_id(token, message_id, react_id):
    '''
    Checks whether a user has an existing react with ID 'react_id' for a given message
    Assumes token is valid, message_id is valid (user is part of channel this message is in),
    and that a react with this ID already exists in the list
    '''
    message_list = get_store()['Messages']
    u_id = get_tokens()[token]
    # locate the message dictionary in question
    for message in message_list:
        if message_id == message['message_id']:
            this_msg = message['message_id']
    for react in this_msg['reacts']:
        if react['react_id'] == react_id:
            if u_id in react['u_ids']:
                return True
    return False


def message_react(token, message_id, react_id):
    '''
    input: valid token, message_id, react_id
    output: {}
    Errors: InputError:
        message_id not valid message within channel that user has joined
        react_id not valid (only valid react ID is 1)
        message with message_id as id already has a react with ID react_id
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    # get database
    data = get_store()
    # getting id of the user
    u_id = get_tokens()[token]
    # check if react id in the list of valid react id's
    if react_id not in [1]:
        raise InputError(description='Not a valid react ID')

    msg_ids = [msg['message_id'] for msg in data['Messages']]
    if message_id not in msg_ids:
        raise InputError(description='Invalid message ID')

    for msg in data['Messages']:
        if msg['message_id'] == message_id:
            # message not in a channel user has joined
            if msg['channel_id'] not in data['Users'][u_id]['channels']:
                raise InputError(description='Not valid message ID within channel you have joined')
            # react list not empty
            if msg['reacts'] != []:
                # new react to be added from scratch; append dictionary of new react
                if react_id not in [react['react_id'] for react in msg['reacts']]:
                    msg['reacts'].append({
                        'react_id': react_id,
                        'u_id': [u_id],
                        'is_this_user_reacted': msg['u_id'] == u_id
                    })
                # existing react: check if user already reacted to this react
                elif has_user_reacted_react_id(token, message_id, react_id):
                    raise InputError(description='Already reacted with this react')
                # adding the react; find the correct react dictionary then appending user
                for react in msg['reacts']:
                    if react['react_id'] == react_id:
                        react['u_ids'].append(u_id)
                        react['is_this_user_reacted'] = msg['u_id'] == u_id
            # react list is empty
            else:
                msg['reacts'].append({
                    'react_id': react_id,
                    'u_id': [u_id],
                    'is_this_user_reacted': msg['u_id'] == u_id
                })
    return {}


def message_unreact(token, message_id, react_id):
    '''
    input: valid token, message_id, react_id
    output: {}
    Errors: InputError:
        message_id not valid message within channel that user has joined
        react_id not valid (only valid react ID is 1)
        message with message_id as id already has a react with ID react_id
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    # get database
    data = get_store()
    # getting id of the user
    u_id = get_tokens()[token]
    # checkif react id in the list of valid react id's
    if react_id not in [1]:
        raise InputError(description='Not a valid react ID')

    msg_ids = [msg['message_id'] for msg in data['Messages']]
    if message_id not in msg_ids:
        raise InputError(description='Invalid message ID')

    for msg in data['Messages']:
        if msg['message_id'] == message_id:
            # message not in a channel user has joined
            if msg['channel_id'] not in data['Users'][u_id]['channels']:
                raise InputError(description='Not valid message ID within channel you have joined')
            
            # message has no existing react by user
            if msg['reacts'] == [] or has_user_reacted_react_id(token, message_id, react_id) is False:
                raise InputError(description='You do not have an existing react to this message')
            # unreact to the message
            for react in msg['reacts']:
                if react['react_id'] == react_id:
                    react['u_ids'].remove(u_id)
                    if u_id == msg['u_id']:
                        react['is_this_user_reacted'] = False

    return {}
