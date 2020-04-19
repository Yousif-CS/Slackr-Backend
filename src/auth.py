'''
This file contains implementations for
authentication functions: register, login and logout, token generation
along with helper functions used in other files as well
'''
#pylint: disable=trailing-whitespace

import hashlib
import jwt


from state import get_store, get_tokens
from is_valid_email import is_valid_email
from error import InputError

SECRET = "Never l3t me g0"
MAX_NAME_LEN = 50
MIN_NAME_LEN = 1
MAX_HANDLE_LEN = 20
MIN_HANDLE_LEN = 2
MIN_PASS_LEN = 6

def verify_token(token):
    '''
    Checks that the token given is in the TOKENS dictionary as described in server.py
    Args: token (str)
    Return: (bool)
    '''
    token_dict = get_tokens()
    if token not in token_dict.keys():
        return False
    return True

def generate_token(u_id):
    '''
    Uses jwt to generate a token
    Args: u_id (int)
    Return: token (str)
    '''
    return jwt.encode({"u_id": u_id}, SECRET, algorithm="HS256").decode('utf-8')

def get_token(u_id):
    '''
    Retrieves token given a user id, returns None if the user is logged out FOR AUTH_LOGOUT
    '''
    tokens = get_tokens()
    for token, logged_uid in tokens.items():
        if logged_uid == u_id:
            return token
    return None


def create_handle(name_first, name_last):
    '''
    Creates a handle using the first and last name of a user.
    Makes sure handles are unique
    '''
    count = 0
    handle_str = name_first.lower() + name_last.lower()
    handle_str = handle_str[:20]

    while is_handle_unique(handle_str) is False:
        count += 1
        handle_str = handle_str[:20 - len(str(count))] + str(count)

    return handle_str


def is_handle_unique(handle_str):
    '''
    Returns true if no other person has the handle
    '''
    data = get_store()
    unique = data.users.handle_unique(handle_str)
    return unique


def auth_register(email, password, name_first, name_last):
    '''
    Given a user's first and last name, email address, and password,
    create a new account for them and return a new token for authentication in their session.
    A handle is generated that is the concatentation of a lowercase-only first name and last name.
    If the concatenation is longer than 20 characters, it is cutoff at 20 characters.
    If the handle is already taken, you may modify the handle in any way you see fit
    to make it unique.

    Output: {u_id, token}
    InputError: invalid email, non-unique email,
    password less than 6 char long, first or last name not [1,50] char long
    '''
    data = get_store()

    # InputError if email not valid
    if is_valid_email(email) is False:
        raise InputError(description="Input is not a valid email")

    # InputError if password is too short (less than 6 char)
    if len(password) < MIN_PASS_LEN:
        raise InputError(
            description="Password too short, must be at least 6 characters")

    if len(name_first) < MIN_NAME_LEN or len(name_last) < MIN_NAME_LEN \
            or len(name_first) > MAX_NAME_LEN or len(name_last) > MAX_NAME_LEN:
        raise InputError(description="Names must be between 1 and 50 characters long inclusive, \
            and cannot contain exclusively whitespaces.")
    
    if name_first.isspace() or name_last.isspace():
        raise InputError(
            description="Names cannot exclusively contain whitespaces.")

    if name_first.lower() == "hangman":
        raise InputError(
            description="First name cannot be any case insensitive version of 'Hangman'")

    if name_last.lower() == "b0t":
        raise InputError(
            description="Last name cannot be any case insensitive version of 'B0T'")

    # hash the password
    encrypted_pass = hashlib.sha256(password.encode()).hexdigest()

    #Adds all user's details to the Database
    details = email, encrypted_pass, name_first, name_last, create_handle(name_first, name_last)
    u_id = data.add_user(details)

    token = generate_token(u_id)
    # Store the token-u_id pair in the temporary TOKEN dictionary
    get_tokens()[token] = u_id

    # return u_id and token
    return {
        "u_id": u_id,
        "token": token
    }


def find_u_id(email):
    '''
    Returns back the user id given the email. If the email does
    not correspond to an existing user in the database => returns None
    '''
    data = get_store()
    return data.users.email_used(email)


def auth_login(email, password):
    '''
    Given a registered users' email and password and generates
    a valid token for the user to remain authenticated.
    InputError: email entered not valid, email does not
    belong to a user, password is incorrect
    Output: u_id, token
    '''
    data = get_store()

    # Ensure user's password matches otherwise raise an error
    encrypted_pass = hashlib.sha256(password.encode()).hexdigest()
    u_id = data.users.validate_login(email, encrypted_pass)

    #check if the user is not already logged in
    token = get_token(u_id)
    if token is not None:
        raise InputError(description='User is already logged on')

    token = generate_token(u_id)
    get_tokens()[token] = u_id
    return {
        "u_id": u_id,
        "token": token
    }


    # Store the token-u_id pair in the temporary TOKEN dictionary


def auth_logout(token):
    '''
    input:valid token
    output: is_success (True / False)
    Must invalidate token to log user out.
    '''
    # verify the user
    if verify_token(token) is False:
        return {'is_success': False}

    #remove the user's token
    get_tokens().pop(token)
    return {'is_success': True}

def auth_passwordreset_request(email):
    '''
    Sends a reset code to a user's email and adds
    the reset code to a dictionary
    Input: User's email
    Returns: None
    '''
    data = get_store()

    if not data.users.email_used(email):
        return {}

    #Generates reset code for user and sends it to their email
    #add reset code to dictionary for user
    data.codes.push(email)

    return {}

def auth_passwordreset_reset(reset_code, new_password):
    '''
    Given a valid reset code change the user's password
    to the new password given
    Input: Reset code and new_password
    Returns: None
    '''
    if len(new_password) < 6:
        raise InputError(
            description="Password too short, must be at least 6 characters")

    data = get_store()

    # Check if reset_code exists within dictionary and return the email key paired with that code
    data.codes.code_exists(reset_code)
    email = data.codes.find_email(reset_code)

    #Retrieve user's id and set their new password
    u_id = data.users.find_u_id(email[0])
    data.users.set_password(u_id, new_password)
    #Delete reset code from the dictionary
    data.codes.delete(email[0])        

    return {}
