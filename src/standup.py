'''
This module contains implementations of standup functions
along with all its related schedulers and data structures
'''
import time
import sched
from server import get_store, get_tokens
from auth import verify_token, get_token, generate_token, auth_logout
from error import InputError, AccessError
from message import message_send

MAX_LENGTH = 1000

#this is a list of standups for each channel
#which contains the channel id, the time it is created, the time it finishes, 
# the creator's user id and the messages it has
standup_messages = []


#this is a scheduler that handles scheduling events for standup_start
my_scheduler = sched.scheduler(time.time, time.sleep)

def getStandup():
    global standup_messages
    return standup_messages

def flush_standup(channel_id):
    '''
    Helper function to concat messages in a standup and send them
    at once
    '''
    standups = getStandup()
    tokens = get_tokens()
    for standup in standups:
        if standup['channel_id'] == channel_id:
            to_remove = standups.pop(standup)
            to_send = '\n'.join(standup['messages'])
            user_token = get_token()
            #the user has logged out: generate a temporary token
            if user_token is None:
                user_token = generate_token()
                message_send(user_token, channel_id, to_send)
                auth_logout(user_token)
            else:
                message_send(user_token, channel_id, to_send)
    
    
def runScheduler(target, time, args):
    my_scheduler.enterabs(time, 1, flush_standup, argument=args)
    my_scheduler.run()

def standup_start(token, channel_id, length):
    '''
    Start a standup in a given channel
    '''
    #verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    #get database information
    data = get_store()
    #getting id of the user
    u_id = get_tokens()[token]

    #verify the channel exists
    if channel_id not in data['Channels']:
        raise AccessError(description="Invalid channel id")
    
    #getting all the standups
    standups_info = getStandup()
    #verify there are currently no standups in the channel
    for standup in standups_info:
        if standup['channel_id'] == channel_id:
            raise InputError(description="Active standup already in channel")
    
    #verifying length is an float or an integer
    if not isinstance(length, int) and not isinstance(length, float):
        raise InputError(description="Invalid length type")
    #creating a new standup
    standups_info.append({
        'channel_id': channel_id,
        'u_id': u_id,
        'time_start': time.time(),
        'time_finish': time.time() + length,
        'messages': [],
    })
    #schedule flushing the standup
    runScheduler(target=flush_standup, time=time.time() + length, args=(channel_id,))


def standup_active(token, channel_id):
    #verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')
    
    #get database information
    data = get_store()
    #getting id of the user
    u_id = get_tokens()[token]

    #verify the channel exists
    if channel_id not in data['Channels']:
        raise AccessError(description="Invalid channel id")
    
    #getting all the standups
    standups_info = getStandup()
    for standup in standups_info:
        if standup['channel_id'] == channel_id:
            return {"is_active":True, "time_finish": standup['finish_time']}
    return {"is_active": False, "time_finish": None}

def standup_send(token, channel_id, message):
    #verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')
    
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

    #verify message is not more than 1000 characters or not less than 1
    if len(message) > MAX_LENGTH or len(message) == 0:
        raise InputError(description="Invalid message")

    #verify there is an active standup
    #getting all the standups
    standups_info = getStandup()
    for standup in standups_info:
        if standup['channel_id'] == channel_id:
            standup['messages'].append(message)
            return {}

    raise InputError(description="No active standup in this channel")