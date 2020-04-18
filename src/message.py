'''
File contains implementations of functions:
- message_send
- message_sendlater
- message_pin
- message_unpin
- message_remove
- message_edit
- message_react
- message_unreact
'''

import sched
from threading import Thread
from time import time, sleep
from state import get_store, get_tokens
from auth import verify_token
from error import InputError, AccessError
from hangman import hangman

MAX_MSG_LEN = 1000

MY_SCHEDULER = sched.scheduler(time, sleep)


def message_send(token, channel_id, message):
    '''
    Sends a message into channel with ID channel_id

    Parameters:
        valid token (str): of authorised user
        channel_id (int): the channel into which the message is to be sent
        message (str): the message to be sent by the authorised user into channel

    Returns: dictionary containing:
        message_id (int): ID assigned to the new message

    Raises:
        InputError: if message length is greater than 1000 strings or message is empty,
            or channel_id is invalid
        AccessError: if token is invalid, or the authorised user is not part of
            the channel with ID channel_id
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

    # Facilitation of Hangman Game
    hbot_output = hangman(message, channel_id, u_id)
    if hbot_output is not None:
        # obtain the token of the hangman bot for the channel we are currently in
        hbot_token = data.channels.get_hbot_details(channel_id)[1]
        message_send(hbot_token, channel_id, hbot_output)

    return {
        'message_id': new_id
    }


def run_scheduler(target, time_sent, args):
    '''
    A helper function to run the scheduler wrapper function to execute message_sendlater

    Parameters:
        target function: name of the function to be run by run_scheduler
        time_sent (float): the unix timestamp for time to execute the action
        arguments (tuple): a collection of arguments to pass into the target
    '''

    MY_SCHEDULER.enterabs(time_sent, 1, action=target, argument=args)
    MY_SCHEDULER.run()

def message_sendlater(token, channel_id, message, time_sent):
    '''
    Sends a message into channel with ID channel_id at a specified time in the future

    Parameters:
        valid token (str): of authorised user
        channel_id (int): the channel into which the message is to be sent
        message (str): the message to be sent by the authorised user into channel
        time_sent (float): unix timestamp of a time in the future for message to be sent

    Returns: dictionary containing:
        message_id (int): ID assigned to the new message

    Raises:
        InputError: if message length is greater than 1000 strings or message is empty,
            or channel_id is invalid, or time_sent is not a correctly formatted future timestamp
        AccessError: if token is invalid, or the authorised user is not part of
            the channel with ID channel_id
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
    Pins the message with ID message_id in the channel that it is in
    Parameters:
        valid token (str): of authorised user
        message_id (int): ID of the message to be pinned

    Returns: empty dictionary

    Raises:
        InputError: if message with ID message_id is not a valid message, or
            message is already pinned
        AccessError: if token is invalid, or if authorised user is not a slackr
            owner nor an admin of the channel in which the message is
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
    Unpins the message with ID message_id in the channel that it is in
    Parameters:
        valid token (str): of authorised user
        message_id (int): ID of the message to be unpinned

    Returns: empty dictionary

    Raises:
        InputError: if message with ID message_id is not a valid message, or
            message is currently unpinned
        AccessError: if token is invalid, or if authorised user is not a slackr
            owner nor an admin of the channel in which the message is
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
    Removes the message with ID message_id from the channel that it is currently in
    Parameters:
        valid token (str): of authorised user
        message_id (int): ID of the message to be removed

    Returns: empty dictionary

    Raises:
        InputError: if message with ID message_id is not a valid message or does not exist
        AccessError: if token is invalid, or if authorised user is not a slackr
            owner nor an admin of the channel in which the message is, and is not the user who
            sent the original message
    '''

    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    # get database
    data = get_store()
    # getting id of the user
    u_id = get_tokens()[token]

    # check whether the message exists
    if not data.messages.message_exists(message_id):
        raise InputError(
            description='Invalid message ID')

    # check if the user has permissions to remove the message
    channel_id = data.user_message.message_channel(message_id)
    if not (data.user_channel.is_owner(u_id, channel_id) or data.admins.is_admin(u_id) \
        or data.user_message.is_sender(message_id, u_id)):
        raise AccessError(
            description='You do not have access to delete this message')

    data.remove_message(message_id)
    return {}


def has_message_edit_permission(auth_u_id, message_id):
    '''
    A helper function  for message_edit which determines whether a user has edit permissions

    Parameters:
        user ID (int): of the user invoking message_edit
        message_id (int): of the message to be edited

    Returns:
        True / False (bool): whether the user has permission to edit the message
    '''

    data = get_store()

    # check if auth user is a slackr owner
    if data.admins.is_admin(auth_u_id):
        return True

    # check if auth user wrote the message
    if data.user_message.is_sender(message_id, auth_u_id):
        return True

    # check if auth user is owner of channel which contains the message
    # find the message
    # find the channel it belongs to
    ch_id = data.user_message.message_channel(message_id)
    return data.user_channel.is_owner(auth_u_id, ch_id)


def message_edit(token, message_id, message):
    '''
    Edits the message with ID message_id in the channel that it is in
    Parameters:
        valid token (str): of authorised user
        message_id (int): ID of the message to be edited
        new message (str): to replace the old message

    Raises:
        InputError: if message with ID message_id is not a valid message or does not exist
        AccessError: if token is invalid, or if authorised user is not a slackr
            owner nor an admin of the channel in which the message is, and is not the user who
            sent the original message
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
    Adds a 'react' to a specified message within a channel from the user
    Parameters:
        valid token (str): of authorised user
        message_id (int): ID of the message to be given a react
        react_id (int): a valid react ID to give to the message

    Raises:
        InputError: if message with ID message_id is not a valid message or does not exist, or
            if react_id is not a valid react, or message already has an existing react of react_id
            given by the current user
        AccessError: if token is invalid, or if the user is not part of the channel in which the
            message is
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
    if not data.user_channel.link_exists(u_id, channel_id):
        raise InputError(
            description='Not valid message ID within channel you have joined')

    data.user_message.react(u_id, message_id, react_id)
    return {}


def message_unreact(token, message_id, react_id):
    '''
    Removes a certain 'react' from a specified message within a channel
    Parameters:
        valid token (str): of authorised user
        message_id (int): ID of the message to be given a react
        react_id (int): a valid react ID to be removed from the message

    Raises:
        InputError: if message with ID message_id is not a valid message or does not exist, or
            if react_id is not a valid react, or message already has no current react of react_id
            from the current user
        AccessError: if token is invalid, or if the user is not part of the channel in which the
            message exists
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
    if not data.user_channel.link_exists(u_id, channel_id):
        raise InputError(
            description='Not valid message ID within channel you have joined')

    data.user_message.unreact(u_id, message_id, react_id)
    return {}
