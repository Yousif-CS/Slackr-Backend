#please edit this file for user functions

import pytest 
from error import InputError
import user
from auth import auth_register, auth_login

def test_user_profile():
    # create user and login
    user1 = register("joshua@gmail.com", "3.14159", "Joshua", "Wang") # returns {u_id, token}
    # check that the function returns the correct dictionary
    assert user_profile(user['token'], user['u_id']) == user1


