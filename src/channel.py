'''
This file contains all the implementations and data relevant to channel functions
'''
#pylint: disable=trailing-whitespace

from state import get_store, get_tokens
from auth import verify_token
from error import InputError, AccessError

MESSAGE_BLOCK = 50
SLACKR_OWNER = 1
SLACKR_MEMBER = 2


def channel_invite(token, channel_id, u_id):
    '''
    Invites a user (with user id u_id) to join a channel with ID channel_id.
    Once invited the user is added to the channel immediately.
    Args: token (str), channel_id (int), u_id (int)
    InputError: channel ID does not correspond to a valid channel; 
    user ID does not refer to a valid user.
    AccessError: authorised user is not already a member of channel with channel ID.
    '''
    # verify the validity of the authorised user's token
    if verify_token(token) is False:
        raise AccessError(description="Invalid token")

    # check that channel_id corresponds to a valid channel
    data = get_store()
    if not data.channels.channel_exists(channel_id):
        raise InputError(
            description="Channel with this channel ID does not exist")

    # check that the authorised user belongs to this valid channel
    auth_u_id = get_tokens()[token]
    if not data.user_channel.is_member(auth_u_id, channel_id):
        raise AccessError(description="The authorised user is not a member of this channel")

    # check that u_id corresponds to a valid user
    if not data.users.user_exists(u_id):
        raise InputError(description="User ID is not valid")

    # add the user with u_id into the channel
    # update the database by adding a link between the user and the channel
    # checks if user is already apart of the channel
    data.user_channel.join_channel(u_id, channel_id)


def channel_details(token, channel_id):
    '''
    Given a Channel with ID channel_id that the authorised user is part of, 
    provide basic details about the channel.
    Args: token (str), channel_id (int)
    InputError: channel_id is not a valid channel
    AccessError: authorised user is not part of the channel with channel_id
    Output: (channel) name, owner_members, all_members
    '''

    data = get_store()

    # verify the token is valid
    if verify_token(token) is False:
        raise AccessError(description="Invalid token")

    if not data.channels.channel_exists(channel_id):
        raise InputError(description='Channel does not exist')

    # check that the authorised user is member of said channel
    auth_u_id = get_tokens()[token]
    if not data.user_channel.is_member(auth_u_id, channel_id):
        raise AccessError(
            description="The authorised user is not a member of channel with this channel ID")

    # Create two lists and append details about owner members of the channel and all its members
    # return the dictionary containing details of the channel
    return {
        "name": data.channels.channel_details(channel_id)['name'],
        "owner_members": data.channel_owners(channel_id),
        "all_members": data.channel_members(channel_id)
    }


def channel_messages(token, channel_id, start):
    '''
    Lists up to 50 messages within 'channel_id', beginning from the message indexed 'start'.
    Args: 
        token (str): of the user authorising this action 
        channel_id (int): of the channel whose messages require displaying 
        start (int): index of the first message to display
    Raises:
        AccessError:
            if token invalid
            if authorised user does not hav permission to view the channel's messages
        InputError:
            if channel_id does not correspond to a valid channel
    Return: List of 50 messages from channel with channel_id
        starting from index 'start', if we reached the end of the list we set the 'end' index to -1
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')
    # get database information
    data = get_store()
    # getting id of the user
    u_id = get_tokens()[token]
    # verify the channel exists
    if not data.channels.channel_exists(channel_id):
        raise InputError(description='Channel does not exist')

    # verify the user is a member of the channel
    if not data.user_channel.is_member(u_id, channel_id):
        raise AccessError(
            description="You do not have permission to view this channel's messages")
    # getting the messages of the channel
    details = channel_id, start
    messages, more = data.channel_messages(u_id, details)
    return {"messages": messages,
            "start": start,
            "end": -1 if not more else start + MESSAGE_BLOCK
            }


def channel_leave(token, channel_id):
    '''
    Allows a user with 'token' to leave the channel with 'channel_id'

    Args: token (str), channel_id (int)
    Raises:
        AccessError:
            if token invalid
            if user with u_id was not a member of the channel in the first place
        InputError:
            if channel_id does not correspond to a valid channel
    Return: an empty dictionary
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    # get database information
    data = get_store()
    # getting id of the user
    u_id = get_tokens()[token]

    # verify the channel exists
    if not data.channels.channel_exists(channel_id):
        raise InputError(description="Invalid channel id")

    # verify the user is a member of the channel
    if not data.user_channel.is_member(u_id, channel_id):
        raise AccessError(description="Cannot leave channel: not a member")

    # deleting the user from the channel list
    data.user_channel.leave_channel(u_id, channel_id)
    return {}


def channel_join(token, channel_id):
    '''
    Allows a user with a valid 'token' to join a public channel with 'channel_id'

    Args: token (str), channel_id (int)
    Raises:
        AccessError:
            if token invalid
            if the channel is private
        InputError:
            if channel_id does not correspond to an existing channel
            if user with u_id is already a member of the channel
    Return: an empty dictionary
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    # get database information
    data = get_store()
    # getting id of the user
    u_id = get_tokens()[token]

    # verify the channel exists
    if not data.channels.channel_exists(channel_id):
        raise InputError(description="Invalid channel id")

    # verify user is not already a member
    if data.user_channel.is_member(u_id, channel_id):
        raise InputError(description="Already a member")

    # verify the channel is public unless user is a slackr owner
    if not data.admins.is_admin(u_id) and data.channels.is_private(channel_id):
        raise AccessError(
            description="Cannot join channel: channel is private")

    # ... joining channel: if admin
    if data.admins.is_admin(u_id):
        data.user_channel.add_owner(u_id, channel_id)
    else:
        data.user_channel.join_channel(u_id, channel_id)


def channel_addowner(token, channel_id, u_id):
    '''
    Promotes user with 'u_id' to an owner of channel with 'channel_id'

    Args:
        token (str): of the user authorising this action
        channel_id (int): of the channel to which to promote the user to owner
        u_id (int): of the user to be promoted
    Raises:
        AccessError:
            if token invalid
            if token does not belong to a user with permission to promote
        InputError:
            if channel_id does not correspond to a valid channel
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    # get database information
    data = get_store()
    # getting id of the user
    u_id_invoker = get_tokens()[token]

    # verify the channel exists
    if not data.channels.channel_exists(channel_id):
        raise InputError(description="Invalid channel id")

    # verify the invoker is either an owner of the channel or an admin
    if not data.admins.is_admin(u_id_invoker) and \
       not data.user_channel.is_owner(u_id_invoker, channel_id):
        raise AccessError(
            description="You do not have privileges to add owners")

    data.user_channel.add_owner(u_id, channel_id)


def channel_removeowner(token, channel_id, u_id):
    '''
    Demote user with 'u_id' from an owner to normal member of channel with 'channel_id'

    Args:
        token (str): of the user authorising this action
        channel_id (int): of the channel to which to demote the user to normal member
        u_id (int): of the user to be demoted
    Raises:
        AccessError:
            if token invalid
            if token does not belong to a user with permission to demote
            if attempting to demote an admin of the slackr
        InputError:
            if channel_id does not correspond to a valid channel
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    # get database information
    data = get_store()
    # getting id of the user
    u_id_invoker = get_tokens()[token]

    # verify the channel exists
    if not data.channels.channel_exists(channel_id):
        raise InputError(description="Invalid channel id")

    # verify the user to remove is not a Slackr owner
    # and the remover has valid privileges
    if not data.admins.is_admin(u_id_invoker) and data.admins.is_admin(u_id):
        raise AccessError(
            description="You do not have permission to remove the current user")

    # verify the invoker is either an owner of the channel or slackr
    if not data.user_channel.is_owner(u_id_invoker, channel_id):
        raise AccessError(
            description="You do not have premission to remove the current user")

    # remove the ownership
    data.user_channel.remove_owner(u_id, channel_id)
