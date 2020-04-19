'''
This module contains implementations of standup functions
along with all its related schedulers and data structures
'''
import time
from threading import Lock, Thread
import sched

from error import InputError, AccessError
from message import message_send
from auth import verify_token, get_token, generate_token, auth_logout
from state import get_store, get_tokens


def get_lock():
    '''
    Give access to STANDUP_LOCK
    '''
    global STANDUP_LOCK  # pylint: disable=global-statement
    return STANDUP_LOCK


def get_standup():
    '''
    Provide access to the standup list
    '''
    global STANDUP_MESSAGES  # pylint: disable=global-statement
    return STANDUP_MESSAGES


MAX_LENGTH = 1000

# this is a list of standups for each channel
# which contains the channel id, the time it is created, the time it finishes
# the creator's user id and the messages it has
STANDUP_MESSAGES = []

# A data lock that prevents different threads from accessing STANDUP_MESSAGES
# at the same time
STANDUP_LOCK = Lock()

# this is a scheduler that handles scheduling events for standup_start
MY_SCHEDULER = sched.scheduler(time.time, time.sleep)


def flush_standup(channel_id):
    '''
    Input: channel_id (int)
    Returns: Nothing
    Purpose: Helper function to concat messages in a standup and send them
    at once
    '''
    with STANDUP_LOCK:
        standups = get_standup()
        try:
            [to_flush] = list(
                filter(
                    lambda x: x['channel_id'] == channel_id,
                    standups))
            to_send = '\n'.join(to_flush['messages'])
            # message is empty.. do not bother
            if not to_send:
                standups.remove(to_flush)
                return
            # get the token given u_id
            user_token = get_token(to_flush['u_id'])
            if user_token is None:
                # generate a temporary token
                user_token = generate_token(to_flush['u_id'])
                get_tokens()[user_token] = to_flush['u_id']
                message_send(user_token, channel_id, to_send)
                auth_logout(user_token)
            else:
                message_send(user_token, channel_id, to_send)
            standups.remove(to_flush)
        except ValueError:
            pass


def run_scheduler(target, running_time, args):
    '''
    A wrapper for the scheduler
    '''
    MY_SCHEDULER.enterabs(running_time, 1, action=target, argument=args)
    MY_SCHEDULER.run()


def standup_start(token, channel_id, length):
    '''
    Input: channel_id: int, length: int
    Returns: a dictionary containing the finish time of the standup
    Raises: InputError, AccessError
    Start a standup in a given channel
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

    # getting all the standups
    standups_info = get_standup()
    # verify there are currently no standups in the channel
    for standup in standups_info:
        if standup['channel_id'] == channel_id:
            raise InputError(description="Active standup already in channel")

    # verifying length is a float or an integer
    if not isinstance(length, int) and not isinstance(length, float):
        raise InputError(description="Invalid length type")
    # creating a new standup
    time_finish = time.time() + length
    with STANDUP_LOCK:
        standups_info.append({
            'channel_id': channel_id,
            'u_id': u_id,
            'time_start': time.time(),
            'time_finish': time_finish,
            'messages': [],
        })
    # schedule flushing the standup
    running_time = time.time() + length
    sched_thread = Thread(target=run_scheduler, args=(
        flush_standup, running_time, (channel_id, )))
    #run_scheduler(target=flush_standup, running_time=time.time() + length, args=(channel_id,))
    sched_thread.start()
    return {'time_finish': time_finish}


def standup_active(token, channel_id):
    '''
    Input: A token and a channel id
    Returns: a dictionary containing keys is_active and time_finish of a certain channel standup
    Purpose: check whether a standup is active in the database
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    # get database information
    data = get_store()

    # verify the channel exists
    if not data.channels.channel_exists(channel_id):
        raise InputError(description="Invalid channel id")

    # getting all the standups
    standups_info = get_standup()
    for standup in standups_info:
        if standup['channel_id'] == channel_id:
            return {"is_active": True, "time_finish": standup['time_finish']}
    return {"is_active": False, "time_finish": None}


def standup_send(token, channel_id, message):
    '''
    Input: A token, a channel id and a message
    Returns: an empty dictionary if a successful message send to the standup in channel occurred
    Purpose: buffer a message in the standup to be sent later
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

    # verify user is within channel
    if not data.user_channel.is_member(u_id, channel_id):
        raise AccessError(
            description="You do not have permission to send a standup message")

    # verify message is not more than 1000 characters or not less than 1
    if len(message) > MAX_LENGTH or not message:
        raise InputError(description="Invalid message")

    # verify there is an active standup
    # getting all the standups
    standups = get_standup()
    with STANDUP_LOCK:
        try:
            [standup] = list(
                filter(
                    lambda x: x['channel_id'] == channel_id,
                    standups))
            standup['messages'].append(message)
        except ValueError:
            raise InputError(description="No active standup in this channel")
