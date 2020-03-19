from time import time
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
    pass

def message_remove(token, message_id):
    pass

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