'''
This file contains implementations for user functions
'''

from state import get_store, get_tokens
from auth import verify_token
from error import InputError, AccessError
from is_valid_email import is_valid_email


def user_profile(token, u_id):
    '''
    input: a token and a user id.
    output: information about their user id, email, first name, last name,
    and handle if a valid user.
    error: AccessError for invalid token, InputError if u_id is invalid.
    '''

    # check validity of user's token
    if verify_token(token) is False:
        raise AccessError(description="Invalid token")

    # check that the u_id of the user whose information the authorised user wants to access is valid
    data = get_store()
    return data.users.user_details(u_id)


def user_profile_setname(token, name_first, name_last):
    '''
    Update the authorised user's first name and last name. No output.
    '''

    # verify token is valid
    if verify_token(token) is False:
        raise AccessError(description="Invalid token")

    # verify that changes to name are allowed
    if len(name_first) < 1 or len(name_last) < 1 \
            or len(name_first) > 50 or len(name_last) > 50:
        raise InputError(description="Names must be between 1 and 50 characters long inclusive, \
            and cannot contain exclusively whitespaces.")
    # another verification that names are not just spaces
    if name_first.isspace() or name_last.isspace():
        raise InputError(
            description="Names cannot exclusively contain whitespaces.")

    # modify name_first and name_last in the database as per the user's changes
    u_id = get_tokens()[token]
    data = get_store()
    data.users.set_first_name(u_id, name_first)
    data.users.set_last_name(u_id, name_last)


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
        raise InputError(
            description="handle_str too short - it must be between 2 and 20 characters inclusive")
    if len(handle_str) > 20:
        raise InputError(
            description="handle_str too long - - it must be between 2 and 20 characters inclusive")

    # verify the new handle_str is unique
    # allow the "change" if the authorised user's new handle_str is identical to their old one.
    u_id = get_tokens()[token]
    data = get_store()

    if data["Users"][u_id]["handle"] != handle_str:
        for identity in data["Users"]:
            if data["Users"][identity]["handle"] == handle_str:
                raise InputError(
                    description="new handle_str not unique to this user")

    # change the handle_str in the database
    data["Users"][u_id]["handle"] = handle_str


def user_profile_setemail(token, email):
    '''
    Update the authorised user's email address
    '''

    # verify that the token is valid
    if verify_token(token) is False:
        raise AccessError(description="Invalid token")

    # InputError if email not valid
    if is_valid_email(email) is False:
        raise InputError(description="Input is not a valid email")

    # InputError if email not unique
    # Allow if the user is simply changing their email to their current email again.
    u_id = get_tokens()[token]
    data = get_store()

    if data.users.email_used(email):
        raise InputError(description="this email is already being used by another user")

    # Change the user's email in the STORE databas if the above hurdles are passed
    data["Users"][u_id]["email"] = email
