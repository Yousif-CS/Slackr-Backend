#please edit this file for user functions

import pytest 
from error import InputError
from user import *
from auth import auth_register, auth_login

# create user jwang and login
user_jwang = auth_register("joshua@gmail.com", "3.14159", "Joshua", "Wang") # returns {u_id, token}

# tests that 'user_profile' returns the information of the user logged in.
def test_user_profile():
    # check that the function returns the correct dictionary
    assert user_profile(user_jwang['token'], user_jwang['u_id']) == \
        {'user': {
        	'u_id': user_jwang['u_id'],
        	'email': 'joshua@gmail.com',
        	'name_first': 'Joshua',
        	'name_last': 'Wang',
        	'handle_str': 'jwang',
            }
        }

# test one user accessing the information of another valid user id
# test invalid user id throwing input error
# what if wrong token?

# tests that authorised user can update their first and last name so long as input is valid
def test_user_profile_setname():

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
