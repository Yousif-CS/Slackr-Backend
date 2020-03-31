'''
Integration tests for auth functions
'''
#pylint: disable=invalid-name
#pylint: disable=missing-function-docstring
#pylint: disable=pointless-string-statement
#pylint: disable=redefined-outer-name
#pylint: disable=singleton-comparison

import pytest
from auth import auth_register, auth_login, auth_logout
from channel import channel_join
from channels import channels_create
from error import InputError, AccessError
from user import user_profile
from other import workspace_reset


'''------------------testing auth_register--------------------'''
# Test valid registration details successfully registers a user


def test_auth_register_correct_details():
    workspace_reset()
    credentials = auth_register(
        'max.smith@gmail.com', 'great_password101', 'Max', 'Smith')
    assert user_profile(credentials['token'], credentials['u_id']) == {
        "user": {
            "u_id": credentials['u_id'],
            "email": "max.smith@gmail.com",
            "name_first": "Max",
            "name_last": "Smith",
            "handle_str": "maxsmith"
        }
    }


# Test that a long name (over 20 characters for first and last) sets the correct handle
def test_auth_register_long_name():
    workspace_reset()
    user_ms_long = auth_register(
        'max.smith@gmail.com', 'great_password101', 'Maximum', 'Smitherinoooooooooos')
    assert user_profile(user_ms_long['token'], user_ms_long['u_id']) == {
        "user": {
            "u_id": user_ms_long['u_id'],
            "email": "max.smith@gmail.com",
            "name_first": "Maximum",
            "name_last": "Smitherinoooooooooos",
            "handle_str": "maximumsmitherinoooo"
        }
    }


# Invalid emails
# 1. only prefix given for email
# 2. bad prefix given for email (symbols other than .)
# 3. only domain given for email
# 4. bad domain
def test_auth_register_invalid_email_only_prefix():
    workspace_reset()
    with pytest.raises(InputError):
        auth_register('maxsmith', 'cryptic_password#1500', 'Max', 'Smith')


def test_auth_register_invalid_email_bad_prefix():
    workspace_reset()
    with pytest.raises(InputError):
        auth_register('maxsmith.com', 'cryptic_password#1500', 'Max', 'Smith')


def test_auth_register_invalid_email_bad_prefix1():
    workspace_reset()
    with pytest.raises(InputError):
        auth_register('max.-smith-@gmail.com',
                      'cryptic_password#1500', 'Max', 'Smith')


def test_auth_register_invalid_email_bad_prefix2():
    workspace_reset()
    with pytest.raises(InputError):
        auth_register('.max@gmail.com',
                      'cryptic_password#1500', 'Max', 'Smith')


def test_auth_register_only_domain():
    workspace_reset()

    with pytest.raises(InputError):
        auth_register('@gmail.com', 'passwordian10', 'Max', 'Smith')


def test_auth_register_bad_domain():
    workspace_reset()
    with pytest.raises(InputError):
        auth_register('max@gmail.z', 'cryptic_password#1500', 'Max', 'Smith')


def test_auth_register_bad_domain1():
    workspace_reset()
    with pytest.raises(InputError):
        auth_register('.max@g@#mail.com',
                      'cryptic_password#1500', 'Max', 'Smith')


def test_auth_register_bad_domain2():
    workspace_reset()
    with pytest.raises(InputError):
        auth_register('max@google.mail',
                      'cryptic_password#1500', 'Max', 'Smith')


def test_auth_register_bad_domain3():
    workspace_reset()
    with pytest.raises(InputError):
        auth_register('max@gmail..com',
                      'cryptic_password#1500', 'Max', 'Smith')

# User already exists


def test_auth_register_existing_user():
    workspace_reset()

    auth_register('max.smith@gmail.com', 'great_password101', 'Max', 'Smith')

    with pytest.raises(InputError):
        auth_register('max.smith@gmail.com',
                      'great_password101', 'Max', 'Smith')


# Invalid Password
def test_auth_register_invalid_password():
    workspace_reset()
    with pytest.raises(InputError):
        auth_register('max.smith@gmail.com', 'abc', 'Max', 'Smith')


def test_auth_register_invalid_password1():
    workspace_reset()
    with pytest.raises(InputError):
        auth_register('max.smith@gmail.com', '', 'Max', 'Smith')


def test_auth_register_invalid_password2():
    workspace_reset()
    with pytest.raises(InputError):
        auth_register('max.smith@gmail.com', '     ', 'Max', 'Smith')


def test_auth_register_invalid_password3():
    workspace_reset()
    with pytest.raises(InputError):
        auth_register('max.smith@gmail.com', ' .$ 1', 'Max', 'Smith')


# First name is too many characters, or empty string
def test_register_invalid_first_name():
    workspace_reset()
    with pytest.raises(InputError):
        auth_register('max.smith@gmail.com',
                      'great_password101', 'c' * 51, 'Smith')


def test_register_invalid_first_name1():
    workspace_reset()
    with pytest.raises(InputError):
        auth_register('max.smith@gmail.com', 'great_password101', '', 'Smoth')


def test_register_invalid_first_name2():
    workspace_reset()
    with pytest.raises(InputError):
        auth_register('max.smith@gmail.com', 'great_password101',
                      ' ' * 50 + 'z', 'Smith')


# Last name is too many characters
def test_register_long_last_name():
    workspace_reset()
    with pytest.raises(InputError):
        auth_register('max.smith@gmail.com',
                      'great_password101', 'Max', 'zz' * 26)


def test_register_long_last_name1():
    workspace_reset()
    with pytest.raises(InputError):
        auth_register('max.smith@gmail.com', 'great_password101', 'Max', '')


def test_register_long_last_name2():
    workspace_reset()
    with pytest.raises(InputError):
        auth_register('max.smith@gmail.com', 'great_password101',
                      'Max', '$L:$%#@O$' * 10)


'''------------------testing auth_login--------------------'''
# Valid user logging in


def test_login():
    workspace_reset()

    user = auth_register('max.smith@gmail.com',
                         'great_password101', 'Max', 'Smith')

    user_logging_in = auth_login('max.smith@gmail.com', 'great_password101')

    assert user['u_id'] == user_logging_in['u_id']


# invalid email login
def test_login_invalid_email():
    '''
    Testing an invalid email
    '''
    with pytest.raises(InputError):
        auth_login('ken-@gmail.com', 'HolaMan')

# Wrong password given


def test_login_password():
    workspace_reset()

    auth_register('max.smith@gmail.com', 'great_password101', 'Max', 'Smith')

    with pytest.raises(InputError):
        auth_login('max.smith@gmail.com', 'poor_password')

# No users registered with email


def test_login_no_user():
    workspace_reset()

    auth_register('max.smith@gmail.com', 'great_password101', 'Max', 'Smith')
    auth_register('bob99@unsw.edu.au', '45&*ght', 'Bob', 'Johnson')
    auth_register('kate58@bigpond.com', 'secret101', 'Kate', 'Perkins')

    with pytest.raises(InputError):
        auth_login('linda70@gmail.com', 'let_me_in')


'''------------------testing auth_logout--------------------'''

# Using user's token the logout is successful


def test_logout_success():
    workspace_reset()

    user = auth_register('max.smith@gmail.com',
                         'great_password101', 'Max', 'Smith')

    user_logging_in = auth_login('max.smith@gmail.com', 'great_password101')

    assert user['u_id'] == user_logging_in['u_id']

    user_token = user_logging_in['token']
    message = auth_logout(user_token)

    assert message['is_success'] == True


# Token is not valid for a user
def test_logout_unsuccessful():
    workspace_reset()

    user = auth_register('max.smith@gmail.com',
                         'great_password101', 'Max', 'Smith')

    user_logging_in = auth_login('max.smith@gmail.com', 'great_password101')

    assert user['u_id'] == user_logging_in['u_id']
    user_token = user_logging_in['token']

    rand_token = user_token + 'a'

    assert user_token != rand_token
    message = auth_logout(rand_token)
    assert message['is_success'] == False

# A logged out user trying to join a channel


def test_logout_join_fails():
    workspace_reset()

    user = auth_register('max.smith@gmail.com',
                         'great_password101', 'Max', 'Smith')
    user2 = auth_register('josh.wang@hotmail.com',
                          'chonkitychonk', 'Josh', 'Wang')

    message = auth_logout(user2["token"])
    assert message['is_success'] == True

    ch_id = channels_create(user["token"], "new-channel", True)["channel_id"]

    with pytest.raises(AccessError):
        channel_join(user2["token"], ch_id)
