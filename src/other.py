#pylint: disable=missing-module-docstring
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
    if permission_id not in list(SLACKR_MEMBER, SLACKR_OWNER):
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