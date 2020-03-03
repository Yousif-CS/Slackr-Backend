# please edit this file for user functions
# reminders: u_id is an int, token is a str

import pytest 
from error import InputError
from user import *
from auth import auth_register, auth_login

'''------------------testing user_profile--------------------'''

# create users jwang and kli, and login
user_jwang = auth_register("joshua@gmail.com", "3.14159", "Joshua", "Wang") # returns {u_id, token}
user_kli = auth_register("ken@gmail.com", "2.71828", "Ken", "Li")

# tests that 'user_profile' returns the information of the user logged in.
def test_user_profile():
    assert user_profile(user_jwang['token'], user_jwang['u_id']) == \
        {'user': {
        	'u_id': user_jwang['u_id'],
        	'email': 'joshua@gmail.com',
        	'name_first': 'Joshua',
        	'name_last': 'Wang',
        	'handle_str': 'jwang',
            }
        }
    assert user_profile(user_kli['token'], user_kli['u_id']) == \
        {'user': {
        	'u_id': user_kli['u_id'],
        	'email': 'ken@gmail.com',
        	'name_first': 'Ken',
        	'name_last': 'Li',
        	'handle_str': 'kli',
            }
        }

# test one user accessing the information of another valid user id
def test_access_other_users_profile():
    # user kli accessing profile of user jwang
    assert user_profile(user_kli['token'], user_jwang['u_id']) == \
        {'user': {
        	'u_id': user_jwang['u_id'],
        	'email': 'joshua@gmail.com',
        	'name_first': 'Joshua',
        	'name_last': 'Wang',
        	'handle_str': 'jwang',
            }
        }

# test that an invalid u_id (string) will throw an InputError
def test_user_profile_invalid_u_id():
    with pytest.raises(InputError):
        user_profile(user_kli['token'], 'abc')

# what if wrong token? access error?

# tests that authorised user can update their first and last name so long as input is valid
def test_user_profile_setname():
    user_profile_setname()

# test that an input error is thrown for each of:
# 1. name_first empty
# 2. name_last empty
# 3. name_first over 50 char
# 4. name_last over 50 char

# test that white spaces for names are accepted

# test that authorised user can update their email address so long as it is valid and unique
def test_user_profile_setemail():
# test that invalid emails throw input error
# test that existing emails throw input error

# test that authorised user can update their handle so long as it is valid and unique (3 char and 20 char)
def test_user_profile_sethandle():
# test that handles too short <3 throw InputError
# test that handles too long >20 throw InputError
# test that non-unique handles throw InputError

def test_users_all():
    tests that it returns a dictionary containing a dictionary of all the users