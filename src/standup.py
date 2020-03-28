'''
This module contains implementations of standup functions
along with all its related schedulers and data structures
'''
import time
import sched
from threading import Lock
from server import get_store, get_tokens
from auth import verify_token, get_token, generate_token, auth_logout
from message import message_send
from error import InputError, AccessError
from message import message_send

MAX_LENGTH = 1000

#this is a list of standups for each channel
#which contains the channel id, the time it is created, the time it finishes
# the creator's user id and the messages it has
STANDUP_MESSAGES = []

#A data lock that prevents different threads from accessing STANDUP_MESSAGES
#at the same time
STANDUP_LOCK = Lock()

#this is a scheduler that handles scheduling events for standup_start
MY_SCHEDULER = sched.scheduler(time.time, time.sleep)

def get_standup():
    '''
    Provide access to the standup list
    '''
    global STANDUP_MESSAGES #pylint: disable=global-statement
    return STANDUP_MESSAGES

def flush_standup(channel_id):
    '''
    Helper function to concat messages in a standup and send them
    at once
    '''
    with STANDUP_LOCK:
        standups = get_standup()
        for standup in standups:
            #get specific standup with channel id
            #TODO: what happens if the condition fails?
            if standup['channel_id'] == channel_id:
                #remove it
                to_remove = standups.remove(standup)
                #prepare messages
                to_send = '\n'.join(to_remove['messages'])
                user_token = get_token(to_remove['u_id'])
                #the user has logged out: generate a temporary token
                if user_token is None:
                    user_token = generate_token(to_remove['u_id'])
                    message_send(user_token, channel_id, to_send)
                    auth_logout(user_token)
                else:
                    message_send(user_token, channel_id, to_send)

def run_scheduler(target, running_time, args):
    '''
    A wrapper for the scheduler
    '''
    MY_SCHEDULER.enterabs(running_time, 1, action=target, argument=args)
    MY_SCHEDULER.run()

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
        raise InputError(description="Invalid channel id")

    #getting all the standups
    standups_info = get_standup()
    #verify there are currently no standups in the channel
    for standup in standups_info:
        if standup['channel_id'] == channel_id:
            raise InputError(description="Active standup already in channel")

    #verifying length is a float or an integer
    if not isinstance(length, int) and not isinstance(length, float):
        raise InputError(description="Invalid length type")
    #creating a new standup
    time_finish = time.time() + length
    with STANDUP_LOCK:
        standups_info.append({
            'channel_id': channel_id,
            'u_id': u_id,
            'time_start': time.time(),
            'time_finish': time_finish,
            'messages': [],
        })
    #schedule flushing the standup
    run_scheduler(target=flush_standup, running_time=time.time() + length, args=(channel_id,))
    return {'time_finish': time_finish}

def standup_active(token, channel_id):
    '''
    Input: A token and a channel id
    Output: a dictionary containing keys is_active and time_finish of a certain channel standup
    '''
    #verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    #get database information
    data = get_store()

    #verify the channel exists
    if channel_id not in data['Channels']:
        raise InputError(description="Invalid channel id")

    #getting all the standups
    standups_info = get_standup()
    for standup in standups_info:
        if standup['channel_id'] == channel_id:
            return {"is_active":True, "time_finish": standup['finish_time']}
    return {"is_active": False, "time_finish": None}

def standup_send(token, channel_id, message):
    '''
    Input: A token, a channel id and a message
    Output: an empty dictionary if a successful message send to the standup in channel occurred
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
        raise InputError(description="Invalid channel id")

    #verify user is within channel
    if u_id not in data['Channels'][channel_id]['users']:
        raise AccessError(description="You do not have permission to send a standup message")

    #verify message is not more than 1000 characters or not less than 1
    if len(message) > MAX_LENGTH or len(message) == 0:
        raise InputError(description="Invalid message")

    #verify there is an active standup
    #getting all the standups
    standups_info = get_standup()
    for standup in standups_info:
        if standup['channel_id'] == channel_id:
            with STANDUP_LOCK:
                standup['messages'].append(message)
            return {}
    raise InputError(description="No active standup in this channel")
