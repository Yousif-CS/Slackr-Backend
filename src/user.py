'''
This file contains implementations for user functions
'''

from server import get_store, get_tokens
from auth import verify_token
from error import InputError, AccessError
from is_valid_email import is_valid_email

def is_u_id_valid(u_id):
    '''
    Helper function for user_profile to check that the u_id is in the database
    '''

    u_ids = []
    for identity in get_store()["Users"].keys():
        u_ids.append(identity)
    if u_id in u_ids:
        return True
    else:
        return False

def user_profile(token, u_id):
    '''
    input: a token and a user id.
    output: information about their user id, email, first name, last name, and handle if a valid user.
    error: AccessError for invalid token, InputError if u_id is invalid.
    '''

    # check validity of user's token
    if verify_token(token) is False:
        raise AccessError(description="Invalid token")

    # check that the u_id of the user whose information the authorised user wants to access is valid
    if is_u_id_valid(u_id) is False:
        raise InputError(description="user id not valid")

    # if so, return the corresponding information by retrieving from the database
    data = get_store()["Users"][u_id]
    user_info = {"user": {
            "u_id": u_id,
            "email": data["email"],
            "name_first": data["name_first"],
            "name_last": data["name_last"],
            "handle_str": data["handle"]
        }
    }

    return user_info

def user_profile_setname(token, name_first, name_last):
    '''
    Update the authorised user's first name and last name. No output.
    '''

    # verify token is valid
    if verify_token(token) is False:
        raise AccessError(description="Invalid token")

    # verify that changes to name are allowed
    if len(name_first) < 1 or len(name_last) < 1 \
        or len(name_first) > 50 or len(name_last) > 50 \
        or name_first.isspace() or name_last.isspace():
        raise InputError(description="Names must be between 1 and 50 characters long inclusive, \
            and cannot contain exclusively whitespaces.")

    # modify name_first and name_last in the database as per the user's changes
    u_id = get_tokens()[token]
    data = get_store()["Users"][u_id]
    data["name_first"] = name_first
    data["name_last"] = name_last

def user_profile_sethandle(token, handle_str):
    '''
    input: token, handle_str
    output: none
    function: updates the authorised user's handle (display name) so long as it is valid
    '''

    # verify the token is valid
    if verify_token(token) is False:
        raise AccessError(description="Invalid token")

    # verify the new handle_str is of the correct length
    if len(handle_str) < 2:
        raise InputError(description="handle_str too short - it must be between 2 and 20 characters inclusive")
    if len(handle_str) > 20:
        raise InputError(description="handle_str too long - - it must be between 2 and 20 characters inclusive")

    # verify the new handle_str is unique
    # allow the "change" if the authorised user's new handle_str is identical to their old one.
    u_id = get_tokens()[token]
    data = get_store()["Users"]

    if data[u_id]["handle"] != handle_str:
        for identity in data:
            if identity["handle"] == handle_str:
                raise InputError(description="new handle_str not unique to this user")

    # change the handle_str in the database
    data[u_id]["handle"] = handle_str

def user_profile_setemail(token, email):
    '''
    Update the authorised user's email address
    '''

    # verify that the token is valid
    if verify_token(token) is False:
        raise AccessError(description="Invalid token")

    # InputError if email not valid
    if is_valid_email(email) is False:
        raise InputError(description="input is not a valid email")

    # InputError if email not unique
    # Allow if the user is simply
    u_id = get_tokens()[token]
    data = get_store()["Users"]

    if email != data[u_id]["email"]:
        for identity in data:
            if identity["email"] == email:
                raise InputError(description="this email is already being used by another user")
    
    # Change the user's email in the STORE databas if the above hurdles are passed
    data[u_id]["email"] = email
    