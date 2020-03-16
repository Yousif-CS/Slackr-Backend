from server import get_store, get_tokens
from auth import verify_token
from error import InputError, AccessError

MESSAGE_BLOCK = 50

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
    messages = sorted(messages, key = lambda message: message['time_created'], reverse = True)
    #reached the end 
    if (start + 50 >= len(messages)):
        return {"messages": messages[start:], "start": start, "end": -1}
    #we return 50 messages with more to give
    return {"messages": messages[start: start + MESSAGE_BLOCK + 1], "start": start, "end": start + MESSAGE_BLOCK + 1}


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
    return {}

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
    
    return {}


