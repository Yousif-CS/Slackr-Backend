'''
This file contains implementations for authentication functions: register, login and logout, token generation
along with helper functions used in other files as well
'''
from server import get_tokens
from error import AccessError

#Auth functions
from server import get_tokens
#please implement this function correctly
def verify_token(token):
    return True

#generates a token for a user and adds him to the global tokens dictionary
def generate_token(u_id):
    pass

#token given a user id, returns None if the user is logged out
def get_token(u_id):
    tokens = get_tokens()
    for token, logged_uid in tokens.items():
        if logged_uid == u_id:
            return token
    return None

def auth_register(email, password, name_first, name_last):
    return {'u_id': 0, 'token': '12313'}

def auth_login(email, password):
    return {'u_id': 0, 'token': '123123'}



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
