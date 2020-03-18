#pylint: disable=missing-module-docstring
from server import get_store, get_tokens
from auth import verify_token
from error import InputError, AccessError

MESSAGE_BLOCK = 50
SLACKR_OWNER = 1
SLACKR_MEMBER = 2

def channel_messages(token, channel_id, start):
    '''
    input: a token, channel_id and the starting index
    output: Return a list of 50 messages from channel with channel_id
            starting from index 'start', if we reached the end of the list
            we set the 'end' index to -1
    '''
    #verify the user
    if verify_token(token) is False:
        raise InputError(description='Invalid token')
    #get database information
    data = get_store()
    #getting id of the user
    u_id = get_tokens()[token]
    #verify the channel exists
    if channel_id not in data['Channels']:
        raise InputError(description="Invalid channel id")
    #verify the user is a member of the channel
    if channel_id not in data['Users'][u_id]['channels']:
        raise AccessError(description="You do not have permission to view this channel's messages")
    #getting the messages of the channel
    message_ids = data['Channels'][channel_id]['messages']
    messages = [message for message in data['Messages'] if message['u_id'] in message_ids]
    #verify the start index is less than the number of messages
    if len(messages) <= start:
        raise InputError(description="Invalid starting index")

    #sorting the message list in terms of time created
    messages = sorted(messages, key=lambda message: message['time_created'], reverse=True)
    #reached the end
    if start + 50 >= len(messages):
        return {"messages": messages[start:], "start": start, "end": -1}
    #we return 50 messages with more to give
    return {"messages": messages[start: start + MESSAGE_BLOCK + 1],
            "start": start,
            "end": start + MESSAGE_BLOCK + 1}


def channel_leave(token, channel_id):
    '''
    input: a token and a channel id
    output: an empty dictionary, and removes user from the channel
    '''
    #verify the user
    if verify_token(token) is False:
        raise InputError(description='Invalid token')

    #get database information
    data = get_store()
    #getting id of the user
    u_id = get_tokens()[token]

    #verify the channel exists
    if channel_id not in data['Channels']:
        raise InputError(description="Invalid channel id")

    #verify the user is a member of the channel
    if channel_id not in data['Users'][u_id]['channels']:
        raise AccessError(description="You do not have permission leave channel: not a member")

    #deleting the user from the channel list
    #and deleting the channel from the user's channel's list
    data['Channels'][channel_id]['all_members'].remove(u_id)
    #removing the user from the owner members if he is an owner, otherwise just pass
    try:
        data['Channels'][channel_id]['owner_members'].remove(u_id)
    except ValueError:
        pass
    data['Users'][u_id]['channels'].remove(channel_id)

def channel_join(token, channel_id):
    '''
    input: a token and a channel_id
    output: an empty dictionary, and adding the user to the channel with channel_id
    '''
    #verify the user
    if verify_token(token) is False:
        raise InputError(description='Invalid token')

    #get database information
    data = get_store()
    #getting id of the user
    u_id = get_tokens()[token]

    #verify the channel exists
    if channel_id not in data['Channels']:
        raise InputError(description="Invalid channel id")

    #verify the channel is public
    if data['Channels'][channel_id]['is_private'] is True:
        raise AccessError(description="Cannot join channel: channel is private")
    
    #adding user to channel details
    #and adding channel to user's channels list
    data['Channels'][channel_id]['all_members'].append(u_id)
    data['Users'][u_id]['channels'].append(channel_id)
    
    #if user is an owner of slackr, then he is added as an owner
    if data['Users'][u_id]['global_permission'] == SLACKR_OWNER:
        data['Channels'][channel_id]['owner_members'].append(u_id)

def channel_addowner(token, channel_id, u_id):
    '''
    input: a token,  a channel_id, and a u_id
    output: add user with u_id as an owner to channel_id
    '''
    #verify the user
    if verify_token(token) is False:
        raise InputError(description='Invalid token')

    #get database information
    data = get_store()
    #getting id of the user
    u_id_invoker = get_tokens()[token]

    #verify the channel exists
    if channel_id not in data['Channels']:
        raise InputError(description="Invalid channel id")

    #verify user to add is not an owner already
    if u_id in data['Channels'][channel_id]['owner_members']:
        raise InputError(description="User is already an owner")

    #verify the invoker is either an owner of the channel or slackr
    if u_id_invoker not in data['Channels'][channel_id]['owner_members'] \
        and data['Users'][u_id_invoker]['global_permission'] != SLACKR_OWNER:
        raise AccessError(description="You do not have privileges to add owners")

    #add user as member if not already
    if u_id not in data['Channels'][channel_id]['all_members']:
        data['Channels'][channel_id]['all_members'].append(u_id)
        data['Users'][u_id]['channels'].append(channel_id)

    #add user as owner
    data['Channels'][channel_id]['owner_members'].append(u_id)

def channel_removeowner(token, channel_id, u_id):
    '''
    input: a token,  a channel_id, and a u_id
    output: user with u_id removed from being an owner to channel_id
    '''
    #verify the user
    if verify_token(token) is False:
        raise InputError(description='Invalid token')

    #get database information
    data = get_store()
    #getting id of the user
    u_id_invoker = get_tokens()[token]

    #verify the channel exists
    if channel_id not in data['Channels']:
        raise InputError(description="Invalid channel id")

    #verify user to remove is an owner
    if u_id not in data['Channels'][channel_id]['owner_members']:
        raise InputError(description="User is not an owner")
    
    #verify the user to remove is not a Slackr owner
    if data['Users'][u_id]['global_permission'] == SLACKR_OWNER:
        raise AccessError(description="You do not have permission to the current user")
    
    #verify the invoker is either an owner of the channel or slackr
    if u_id_invoker not in data['Channels'][channel_id]['owner_members'] \
        and data['Users'][u_id_invoker]['global_permission'] != SLACKR_OWNER:
        raise AccessError(description="You do not have premission to remove owners")
    
    #remove the ownership
    data['Channels'][channel_id]['owner_members'].remove(u_id)



    
