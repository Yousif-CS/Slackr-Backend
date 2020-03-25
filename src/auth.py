'''
This file contains implementations for authentication functions: register, login and logout, token generation
along with helper functions used in other files as well
'''
from server import get_tokens
from error import AccessError

from server import get_store, get_tokens
from is_valid_email import is_valid_email
from error import InputError, AccessError
import jwt 
import hashlib

SECRET = "Never l3t me g0"

# checks that the token given is in the TOKENS dictionary as described in server.py
def verify_token(token):
    token_dict = get_tokens()
    if token not in token_dict.keys():
        return False
    return True

# generates a token for a user and adds him to the global tokens dictionary
def generate_token(u_id):
    return jwt.encode({"u_id": u_id}, SECRET, algorithm="HS256").decode('utf-8')

# retrieves token given a user id, returns None if the user is logged out FOR AUTH_LOGOUT
def get_token(u_id):
    tokens = get_tokens()
    for token, logged_uid in tokens.items():
        if logged_uid == u_id:
            return token
    return None

def create_handle(name_first, name_last):
    data = get_store()
    count = 0
    handle_str = name_first.lower() + name_last.lower()
    handle_str = handle_str[:20]
    
    while is_handle_unique(handle_str) is False:
        count += 1
        handle_str = handle_str[:20 - len(str(count))] + str(count)

    return handle_str

def is_handle_unique(handle_str):
    data = get_store()
    for identity in data["Users"]:
        if data["Users"][identity]["handle"] == handle_str:
            return False
    return True

def auth_register(email, password, name_first, name_last):
    '''
    Given a user's first and last name, email address, and password, 
    create a new account for them and return a new token for authentication in their session. 
    A handle is generated that is the concatentation of a lowercase-only first name and last name. 
    If the concatenation is longer than 20 characters, it is cutoff at 20 characters. 
    If the handle is already taken, you may modify the handle in any way you see fit to make it unique.

    Output: {u_id, token}
    InputError: invalid email, non-unique email, password less than 6 char long, first or last name not [1,50] char long
    '''
    data = get_store()
    
    # InputError if email not valid
    if is_valid_email(email) is False:
        raise InputError(description="Input is not a valid email")
    
    # If this is the first user, then they become the slack owner, and have u_id of 1, and have global_permissions.
    if len(data["Slack_owners"]) == 0:
        u_id = 1
        data["Users"] = {}
        data["Users"][u_id] = {}
        data["Users"][u_id]["global_permission"] = 1
    else:
        u_id = max(data["Users"].keys()) + 1
        data["Users"][u_id] = {}
        data["Users"][u_id]["global_permission"] = 2

        # InputError if email not unique
        for identity in data["Users"].values():
            if identity["email"] == email:
                raise InputError(description="This email is already being used by another user")
    

    # InputError if password is too short (less than 6 char)
    if len(password) < 6:
        raise InputError(description="Password too short, must be at least 6 characters")

    # Length of name too long or too short
    if len(name_first) < 1 or len(name_last) < 1 \
        or len(name_first) > 50 or len(name_last) > 50 \
        or name_first.isspace() or name_last.isspace():
        raise InputError(description="Names must be between 1 and 50 characters long inclusive, \
            and cannot contain exclusively whitespaces.")

    # hash the password
    encrypted_pass = hashlib.sha256(password.encode()).hexdigest()

    # put all the information (email, password, name_first, name_last, handle) into database.p
    data["Users"][u_id]["name_first"] = name_first
    data["Users"][u_id]["name_last"] = name_last
    data["Users"][u_id]["email"] = email
    data["Users"][u_id]["password"] = encrypted_pass
    data["Users"][u_id]["handle"] = ""
    data["Users"][u_id]["handle"] = create_handle(name_first, name_last)
    data["Users"][u_id]["channels"] = []

    token = generate_token(u_id)
    
    # Store the token-u_id pair in the temporary TOKEN dictionary
    get_tokens()[token] = u_id

    # generate and return u_id and token
    return {
        "u_id": u_id,
        "token": token
    }

def find_u_id(email):
    data = get_store()

    for identity in data["Users"]:
        if email == identity["email"]:
            return identity
    return None
    

def auth_login(email, password):
    '''
    Given a registered users' email and password and generates a valid token for the user to remain authenticated.
    InputError: email entered not valid, email does not belong to a user, password is incorrect
    Output: u_id, token
    '''
    data = get_store()

    if is_valid_email(email) is False:
        raise InputError(description='Email is not a valid email')
    
    u_id = find_u_id(email)
    if u_id is None:
        raise InputError(description='Email does not belong to a registered user')
    
    if hashlib.sha256(password.encode()).hexdigest() != data["Users"][u_id]["password"]:
        raise InputError(description='Password incorrect')

    token = generate_token(u_id)
    
    # Store the token-u_id pair in the temporary TOKEN dictionary
    get_tokens()[token] = u_id

    return {
        "u_id": u_id,
        "token": token
    }


def auth_logout(token):
    '''
    input:valid token
    output: is_success (True / False)
    Must invalidate token to log user out.
    '''
    # verify the user
    if verify_token(token) is False:
        raise AccessError(description='Invalid token')

    tokens = get_tokens()
    u_id = get_tokens()[token]
    # removing the key value pair from TOKENS
    del tokens[token]
    # checking if user is logged out
    if get_token(u_id) is None:
        return True
    else: return False
