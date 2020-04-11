'''
Implementations of message functionalities
'''

import sched
from threading import Thread
from time import time, sleep
from state import get_store, get_tokens
from auth import verify_token
from error import InputError, AccessError

MAX_MSG_LEN = 1000

MY_SCHEDULER = sched.scheduler(time, sleep)


def message_send(token, channel_id, message):
    '''
    input: valid token, channel_id to send message into, actual message string
    output: a globally unique message_id in dictionary
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    # checking message string is valid
    if not isinstance(message, str) or len(message) > MAX_MSG_LEN or len(message) == 0:
        raise InputError(description='Invalid message')

    # get database
    data = get_store()
    # getting id of the user
    u_id = get_tokens()[token]

    # checking channel_id is valid (user is part of)
    if not data.user_channel.link_exists(u_id, channel_id):
        raise AccessError(
            description='You do not have access to send messages in this channel')

    # send the message
    details = message, time()
    new_id = data.add_message(u_id, channel_id, details)
    return {
        'message_id': new_id
    }


# set up scheduler wrapper function
def run_scheduler(target, time_sent, args):
    '''
    Wrapper for scheduler
    '''
    MY_SCHEDULER.enterabs(time_sent, 1, action=target, argument=args)
    MY_SCHEDULER.run()

def message_sendlater(token, channel_id, message, time_sent):
    '''
    input: valid token, channel_id, message and time in the future
    output: {message_id};
    Sends message from user to channel (specified by id) at specific time, automatically
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')
    # checking message string is valid
    if not isinstance(message, str) or len(message) > MAX_MSG_LEN or len(message) == 0:
        raise InputError(description='Invalid message')

    # get database
    data = get_store()
    # getting id of the user
    u_id = get_tokens()[token]

    # checking channel_id is valid (user is part of)
    if not data.user_channel.link_exists(u_id, channel_id):
        raise AccessError(
            description='You do not have access to send message in this channel')
    # checking time_sent is valid (it is a time in the future)
    if time_sent < time():
        raise InputError(description='Scheduled send time is invalid')

    # assigning new ID for the message
    new_id = data.messages.next_id()

    # the action to be completed at time time_sent
    sched_thread = Thread(target=run_scheduler, args=(
        message_send, time_sent, (token, channel_id, message, )))
    # run the schedular (target=message_send, time_sent=time_sent, )
    sched_thread.start()

    return {
        'message_id': new_id
    }


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

    data.pin(u_id, message_id)
    return {}


def message_unpin(token, message_id):
    '''
    input: token, message_id
    output: {}
    Given message within a channel, remove its pinned status
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    # get database
    data = get_store()
    # getting id of the user
    u_id = get_tokens()[token]

    data.unpin(u_id, message_id)
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

    if not data.messages.message_exists(message_id):
        raise InputError(
            description='Invalid message ID')

    channel_id = data.user_message.message_channel(message_id)
    if not (data.user_channel.is_owner(u_id, channel_id) or data.admins.is_admin(u_id) \
        or data.user_message.is_sender(message_id, u_id)):
        raise AccessError(
            description='You do not have access to delete this message')

    data.remove_message(message_id)
    return {}


def has_message_edit_permission(auth_u_id, message_id):
    '''
    Check if user is the sender, or an admin or an owner of the channel
    '''
    data = get_store()

    # check if auth user is a slackr owner
    if data.admins.is_admin(auth_u_id):
        return True

    # check if auth user wrote the message
    if data.user_message.is_sender(auth_u_id, message_id):
        return True

    # check if auth user is owner of channel which contains the message
    # find the message
    # find the channel it belongs to
    ch_id = data.user_message.message_channel(message_id)
    if data.user_channel.is_owner(auth_u_id, ch_id):
        return True
    else:
        return False

def message_edit(token, message_id, message):
    '''
    Given a message, update it's text with new text. If the new message
    is an empty string, the message is deleted.
    Empty message string: delete message.
    AccessError if request is not made by: authorised user OR
    (admin or owner) of (channel or slacker).
    '''

    # verify the validity of the token
    if verify_token(token) is False:
        raise AccessError(description="Invalid token")

    # check that the request is being made by a user with the correct permissions
    auth_u_id = get_tokens()[token]
    data = get_store()

    if has_message_edit_permission(auth_u_id, message_id) is False:
        raise AccessError(
            description="User with this u_id does not have permission to edit this message")

    # delete the message if the message string is empty,
    # otherwise modify the message accordingly in both
    # the "Channels" and "Messages" sub-dictionaries
    if message == "":
        message_remove(token, message_id)
    else:
        data.messages.edit(message_id, message)


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

    channel_id = data.user_message.message_channel(message_id)
    if not data.user_channel.link_exists(u_id, channel_id):
        raise InputError(
            description='Not valid message ID within channel you have joined')

    data.user_message.react(u_id, message_id, react_id)
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

    channel_id = data.user_message.message_channel(message_id)
    if not data.user_channel.link_exists(u_id, channel_id):
        raise InputError(
            description='Not valid message ID within channel you have joined')

    data.user_message.unreact(u_id, message_id, react_id)
    return {}
