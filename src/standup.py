#pylint: disable=missing-module-docstring
from server import get_store, get_tokens
from auth import verify_token
from error import InputError, AccessError

MAX_LENGTH = 1000

#this is a list of standups for each channel
#which contains the channel id, the time it is created, the time it finishes, 
# the creator's user id and the messages it has
standup_messages = []

def getStandup():
    global standup_messages
    return standup_messages

def standup_active(token, channel_id):
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
    
    #getting all the standups
    standups_info = getStandup()
    for standup in standups_info:
        if standup['channel_id'] == channel_id:
            return {"is_active":True, "time_finish": standup['finish_time']}
    return {"is_active": False, "time_finish": None}

def standup_send(token, channel_id, message):
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

    #verify user is within channel
    if u_id not in data['Channels'][channel_id]['users']:
        raise AccessError(description="You do not have permission to send a standup message")

    #verify message is not more than 1000 characters
    if len(message) > MAX_LENGTH:
        raise InputError(description="Message is too long")

    #verify there is an active standup
    #getting all the standups
    standups_info = getStandup()
    for standup in standups_info:
        if standup['channel_id'] == channel_id:
            standup['messages'].append(message)
            return {}

    raise InputError(description="No active standup in this channel")