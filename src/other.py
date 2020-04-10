'''
This file contains implementations of miscellaneous functions
that do not belong to a specific category
'''

import pickle
from standup import get_standup, get_lock
from state import get_store, get_tokens, Database
from auth import verify_token, get_token
from error import InputError, AccessError

SLACKR_OWNER = 1
SLACKR_MEMBER = 2


def userpermission_change(token, u_id, permission_id):
    '''
    input: a token, a user id and a permission id
    output: Changes the global permissions of the user to permission_id
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')
    # get database information
    data = get_store()
    # getting id of the user
    u_id_invoker = get_tokens()[token]

    # verify that u_id is a valid user
    if data.users.user_exists(u_id):
        raise InputError(description="User does not exist")

    # verify permission_id is valid (1 or 2)
    if not data.admins.is_valid_permission(permission_id):
        raise InputError(description="Invalid permission id")

    # verify the invoker is an admin
    if not data.admins.is_admin(u_id_invoker):
        raise AccessError(
            description="You do not have permission to change permissions")

    # set new permissions
    if permission_id == SLACKR_OWNER:
        data.admins.add(u_id)
    else:
        data.admins.remove(u_id)

def user_remove(token, u_id):
    '''
    Removes a user from slackr
    Arguments: token and u_id of user to be removed
    Returns: empty dictionary, but the user is entirely removed.
    Exceptions: InputError: u_id is not a valid user
                AccessError: remover is not an admin
    Assumptions: removing the user means removing all traces of him including his messages
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    data = get_store()
    # getting id of the user
    u_id_invoker = get_tokens()[token]

    # verify the invoker is an admin
    if not data.admins.is_admin(u_id_invoker):
        raise AccessError(
            description="You do not have permission to change permissions")

    if not data.users.user_exists(u_id):
        raise InputError(description="Invalid user id")

    #removing his user details
    data.users.remove(u_id)
    #removing all his subscriptions to channels
    data.user_channel.remove_link_by_user(u_id)
    #removing all the messages sent by that user
    data.remove_messages(u_id)
    #remove the user the token store if he is logged on
    token = get_token(u_id)
    if token is not None:
        get_tokens().pop(token)

    
def users_all(token):
    '''
    Returns a list of all users and their associated details.
    '''

    # verify the token is valid
    if verify_token(token) is False:
        raise AccessError(description="invalid token")

    # return a dictionary which contains one key, "users", which is itself a list of dictionaries
    # containing types u_id, email, name_first, name_last, handle_str
    data = get_store() 

    return {"users": data.users.all()}


def search(token, query_str):
    '''
    Given a query string, return a collection of messages
    in all of the channels that the user has joined that match the query.
    Results are sorted from most recent message to least recent message
    output: a dictionary, which contains a key "messages",
    which is a list of dictionaries containing types
    { message_id, u_id, message, time_created, reacts, is_pinned  }
    '''
    # verify the token is valid
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    data = get_store()
    auth_u_id = get_tokens()[token]

    if len(query_str) > 1000:
        raise InputError(description="query_str over 1000 characaters; too long")

    matching_msgs = {"messages": []}
    # empty query_str returns an empty list
    if query_str == "":
        return matching_msgs

    # find all the channels the user is a part of and search for query_str in the messages
    for ch_id in data.user_channel.user_channels(auth_u_id):
        msg_ids = data.user_message.channel_all_messages(ch_id)
        for msg_dict in data.messages.all():
            if msg_dict["message_id"] in msg_ids and query_str in msg_dict["message"]:
                matching_msgs["messages"].append({
                    "message_id": msg_dict["message_id"],
                    "u_id": auth_u_id,
                    "message": msg_dict["message"],
                    "time_create": msg_dict["time_created"],
                    "reacts": data.user_message.fetch_message_reacts(msg_dict["message_id"]),
                    "is_pinned": msg_dict["is_pinned"]
                })

    return matching_msgs


def workspace_reset():
    '''
    Resets the workspace state. Assumes that the base state of database.p is:
    {"Users": {}, "Slack_owners": [], "Channels":{}, "Messages": []}
    '''
    # clear the tokens dictionary
    get_tokens().clear()

    # clear database.p
    data = get_store()
    data.reset()
    # clear standups
    with get_lock():
        standups = get_standup()
        standups.clear()

    with open("database.p", "wb") as database_file:
        pickle.dump(data, database_file)
