'''
This file contains all the implementations and data relevant to channel functions
'''

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
    InputError: channel ID does not correspond to a valid channel; user ID does not refer to a valid user.
    AccessError: authorised user is not already a member of channel with channel ID.
    '''
    # verify the validity of the authorised user's token
    if verify_token(token) is False:
        raise AccessError(description="Invalid token")

    # check that channel_id corresponds to a valid channel
    data = get_store()
    if not data.channels.channel_exists(channel_id):
        raise InputError(description="Channel with this channel ID does not exist")

    # check that the authorised user belongs to this valid channel
    auth_u_id = get_tokens()[token]
    if not data.user_channel.is_member(auth_u_id, channel_id):
        raise AccessError(description="The authorised user is not a member of channel with this channel ID")

    # check that u_id corresponds to a valid user
    if not data.users.user_exists(u_id):
        raise InputError(description="User ID is not valid")

    # add the user with u_id into the channel
    # update the database by adding a link between the user and the channel
    #checks if user is already apart of the channel
    data.user_channel.join_channel(u_id, channel_id)

def channel_details(token, channel_id):
    '''
    Given a Channel with ID channel_id that the authorised user is part of, provide basic details about the channel.
    InputError: channel_id is not a valid channel
    AccessError: authorised user is not part of the channel with channel_id
    Output: (channel) name, owner_members, all_members
    '''

    data = get_store()

    # verify the token is valid
    if verify_token(token) is False:
        raise AccessError(description="Invalid token")

    # checks if channel_id exists and returns the name of the channel
    name = data.channels.channel_details(channel_id)

    # check that the authorised user is member of said channel
    auth_u_id = get_tokens()[token]
    if not data.user_channel.is_member(auth_u_id, channel_id):
        raise AccessError(description="The authorised user is not a member of channel with this channel ID")

    owner_ids = data.user_channel.owners(channel_id)
    member_ids = data.user_channel.members(channel_id)

    #Create two lists and append details about owner members of the channel and all its members
    lst_owner_membs = []
    for own_id in owner_ids:
        #retrieve user's details given their id
        user_details = data.users.user_details(own_id)
        lst_owner_membs.append(
            {
                'u_id': own_id,
                'name_first': user_details['name_first'],
                'name_last': user_details['name_last']
            }
        )

    lst_all_membs = []
    for mem_id in member_ids:
        user_details = data.users.user_details(mem_id)
        lst_all_membs.append(
            {
                'u_id': mem_id,
                'name_first': user_details['name_first'],
                'name_last': user_details['name_last']
            }
        )

    # return the dictionary containing details of the channel
    return {
        "name": name['name'],
        "owner_members": lst_owner_membs,
        "all_members": lst_all_membs
    }


def channel_messages(token, channel_id, start):
    '''
    input: a token, channel_id and the starting index
    output: Return a list of 50 messages from channel with channel_id
            starting from index 'start', if we reached the end of the list
            we set the 'end' index to -1
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
    print(len(messages))
    print(len(data.messages.all()))
    return {"messages": messages,
            "start": start,
            "end": -1 if not more else start + MESSAGE_BLOCK
           }


def channel_leave(token, channel_id):
    '''
    input: a token and a channel id
    output: an empty dictionary, and removes user from the channel
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
    input: a token and a channel_id
    output: an empty dictionary, and adding the user to the channel with channel_id
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
        raise AccessError(description="Cannot join channel: channel is private")

    #... joining channel: if admin
    if data.admins.is_admin(u_id):
        data.user_channel.add_owner(u_id, channel_id)
    else:
        data.user_channel.join_channel(u_id, channel_id)

def channel_addowner(token, channel_id, u_id):
    '''
    input: a token,  a channel_id, and a u_id
    output: add user with u_id as an owner to channel_id
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
    input: a token,  a channel_id, and a u_id
    output: user with u_id removed from being an owner to channel_id
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