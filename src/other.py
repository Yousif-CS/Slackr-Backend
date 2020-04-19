'''
This file contains implementations of miscellaneous functions
that do not belong to a specific category
'''
#pylint: disable=trailing-whitespace

import pickle
from standup import get_standup, get_lock
from state import get_store, get_tokens
from auth import verify_token, get_token
from error import InputError, AccessError
from user import user_profile

SLACKR_OWNER = 1
SLACKR_MEMBER = 2


def userpermission_change(token, u_id, permission_id):
    '''
    Sets the user's permission to either owner/admin (1) or normal member (2).

    Args:
        token (str): of the user authorising this action
        u_id (int): of the user whose permission is being changed
        permission_id (int): 1 for owner, 2 for member

    Raises:
        AccessError:
            if token is invalid
            if the user invoking this action is not an owner/admin of the slackr
            if the owner/admin attempts to demote themselves to a normal member
        InputError:
            if u_id does not correspond to an existent user
            if permission_id does not correspond to a valid permission
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')
    # get database information
    data = get_store()
    # getting id of the user
    u_id_invoker = get_tokens()[token]

    # verify that u_id is a valid user
    if not data.users.user_exists(u_id):
        raise InputError(description="User does not exist")

    # verify permission_id is valid (1 or 2)
    if not data.admins.is_valid_permission(permission_id):
        raise InputError(description="Invalid permission id")

    # verify the invoker is an admin
    if not data.admins.is_admin(u_id_invoker):
        raise AccessError(
            description="You do not have permission to change permissions")

    # the admin cannot demote himself
    if u_id_invoker == u_id and permission_id == SLACKR_MEMBER:
        raise InputError(description='Cannot demote current user')

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

    # verify the admin is not removing himself
    if u_id == u_id_invoker:
        raise InputError(description='Cannot remove current user')

    # cannot remove the hangman bot
    if user_profile(token, u_id)['user']['name_first'] == 'Hangman':
        raise InputError(description='Cannot remove Hangman B0T')

    # removing his user details
    data.users.remove(u_id)
    # removing all his subscriptions to channels
    data.user_channel.remove_link_by_user(u_id)
    # removing all the messages sent by that user
    data.remove_messages(u_id)
    # remove the user the token store if he is logged on
    token = get_token(u_id)
    if token is not None:
        get_tokens().pop(token)


def users_all(token):
    '''
    Lists all users on the slackr
    Args: token (str)
    Raises: AccessError if token is invalid
    Returns: a dictionary containing a list of all users and their associated details -
        u_id, email, name_first, name_last, handle_str
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
    Searches all channels which invoking user is part of
    for messages containing the query string.

    Args:
        token (str): of the use authorising this action

    Raises:
        AccessError: if token is invalid
        InputError: if query_str is over 1000 char long

    Returns:
        Dictionary: containing a list of message dictionaries containing
            information of each message that contains the query_str -
            {message_id, u_id, message, time_created, reacts, is_pinned}
    '''
    # verify the token is valid
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    data = get_store()
    auth_u_id = get_tokens()[token]

    if len(query_str) > 1000:
        raise InputError(
            description="query_str over 1000 characaters; too long")

    # empty query_str returns an empty list
    if query_str == "":
        return {
            'messages': []
        }

    # find all the channels the user is a part of and search for query_str in
    # the messages
    return {
        'messages': data.message_search(auth_u_id, query_str)
    }


def workspace_reset():
    '''
    Resets the workspace state. Assumes that the base state of database.p has a Database() instance.
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
