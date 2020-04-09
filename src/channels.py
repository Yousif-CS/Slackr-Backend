'''
This file contains implementation for channels functions
'''
from state import get_store, get_tokens
from auth import verify_token
from error import InputError, AccessError


def channels_list(token):
    '''
    Provides users with details of all channels the requesting user is part of
    Parameter: authorised token
    Returns: list of channels (and associated details) that the authorised user is part of
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    # get database
    data = get_store()
    # getting id of the user
    # get_tokens() should return a dictionary where token key corresponds to that user's id
    u_id = get_tokens()[token]

    # return details about all channels the user is part of
    all_channels = data.channels.all()
    user_channels = data.user_channels.user_channels(u_id)
    # filtered list
    in_channels = [d for d in all_channels if d['channel_id'] in user_channels]
    return {
        'channels': in_channels
    }


def channels_listall(token):
    '''
    Provides users with details of all channels existing in Slackr
    Parameter: token
    Returns: list of ALL channels in Slackr
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    # get database
    data = get_store()

    # return all existing channels
    all_channels = data.channels.all()
    return {
        'channels': all_channels
    }


def channels_create(token, name, is_public):
    '''
    Input: token, name, is_public status
    Output: {channel_id}, creates a new channel with the input name and public / private
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    # get database
    data = get_store()
    # getting user id from token
    u_id = get_tokens()[token]

    # check if name is valid
    if not isinstance(name, str) or len(name) > 20:
        raise InputError(description='Invalid channel name')

    # check if is_public is correct type
    if not isinstance(is_public, bool):
        raise InputError(description='Invalid channel status')

    # creating new channel
    details = name, is_public
    new_id = data.add_channel(u_id, details)
    return {
        'channel_id': new_id
    }
