'''
This file contains implementations of miscellaneous functions that do not belong to a specific category
'''

from server import get_store, get_tokens

from auth import verify_token
from error import InputError, AccessError

SLACKR_OWNER = 1
SLACKR_MEMBER = 2

def userpermission_change(token, u_id, permission_id):
    '''
    input: a token, a user id and a permission id
    output: Changes the global permissions of the user to permission_id
    '''
    #verify the user
    if verify_token(token) is False:
        raise InputError(description='Invalid token')
    #get database information
    data = get_store()
    #getting id of the user
    u_id_invoker = get_tokens()[token]

    #verify that u_id is a valid user
    if u_id not in data['Users']:
        raise InputError(description="User does not exist")

    #verify permission_id is valid (1 or 2)
    if not isinstance(permission_id, int) or permission_id not in list(SLACKR_MEMBER, SLACKR_OWNER):
        raise InputError(description="Invalid permission id")

    #verify the invoker is an admin
    if data['Users'][u_id_invoker]['global_permission'] != SLACKR_OWNER:
        raise AccessError(description="You do not have permission to change permissions")

    #set new permissions
    data['Users'][u_id]['global_permission'] = permission_id

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
    every_user = {"users": []}
    for identity in data["Users"]:
        every_user["users"].append(
            {
                "u_id": identity,
                "email": identity["email"],
                "name_first": identity["name_first"],
                "name_last": identity["name_last"],
                "handle_str": identity["handle"]
            }
        )

    return every_user

def search(token, query_str):
    '''
    Given a query string, return a collection of messages
    in all of the channels that the user has joined that match the query.
    Results are sorted from most recent message to least recent message
    output: a dictionary, which contains a key "messages", which is a list of dictionaries containing types
    { message_id, u_id, message, time_created, reacts, is_pinned  }
    '''

    # verify the token is valid
    if verify_token(token) is False:
        raise InputError(description='Invalid token')
    
    matching_msgs = {"messages": []}
    # empty query_str returns an empty list
    if query_str == "":
        return matching_msgs

    # search for the query_str in the messages
    data = get_store()
    for msg_dict in data["Messages"]:
        if query_str in msg_dict["message"]:
            matching_msgs["messages"].append(
                {
                    "message_id": msg_dict["message_id"],
                    "u_id": msg_dict["u_id"],
                    "message": msg_dict["message"],
                    "time_created": msg_dict["time_created"],
                    "reacts": msg_dict["reacts"],
                    "is_pinned": msg_dict["is_pinned"]
                }
            )

    return matching_msgs
