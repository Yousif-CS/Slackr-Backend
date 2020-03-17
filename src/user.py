from server import get_store, get_tokens
from auth import verify_token
from error import InputError, AccessError

def is_u_id_valid(u_id):
    u_ids = []
    for id in get_store()["Users"].keys():
        u_ids.append(id)
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
        raise AccessError(description = "Invalid token")

    # check that the u_id of the user whose information the authorised user wants to access is valid
    if is_u_id_valid(u_id) is False:
        raise InputError(description = "user id not valid")

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
