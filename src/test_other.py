# please write tests for users_all and search here

import pytest 
from other import users_all, search
from user import user_profile
from auth import auth_register, auth_login, auth_logout
from channels import channels_create
from message import message_send
from error import InputError, AccessError

@pytest.fixture
def make_user_ab():
    user_ab = auth_register("alice@gmail.com", "stronkpassword123", "Alice", "Bee")
    return user_ab

@pytest.fixture
def make_user_cd():
    user_cd = auth_register("charlie@gmail.com", "comp1531pass", "Charlie", "Dee")
    return user_cd


# These users are designed for the users_all function for Josh
@pytest.fixture
def make_user_ef():
    user_ef = auth_register("edward@gmail.com", "12345687", "Edward", "Frankenstein")
    return (user_ef["token"], user_ef["u_id"])

@pytest.fixture
def make_user_gh():
    user_gh = auth_register("gregory@gmail.com", "ihaveadream", "Gregory", "Heidelberg")
    return (user_gh["token"], user_ef["u_id"])

@pytest.fixture
def make_user_ij():
    user_ij = auth_register("ian@hotmailcom", "stretchy0urh4mstrinG5thr1c3", "Ian", "Jacobs")
    return (user_ij["token"], user_ij["u_id"])
###

@pytest.fixture
def create_public_channel(make_user_ab):
    user_ab = make_user_ab
    channel_id = channels_create(user_ab['token'], 'test_channel_public', True)    
    return (channel_id, user_ab)

@pytest.fixture
def create_private_channel(make_user_ab):
    user_ab = make_user_ab
    channel_id = channels_create(user_ab['token'], 'test_channel_private', False) 
    return (channel_id, user_ab)

'''------------------testing users_all--------------------'''
# returns a dictionary of a list containing all the users

# start with only one user accessing all users

def test_users_all_one_user(make_user_ef):
    ef_token, ef_u_id = make_user_ef

    assert users_all(ef_token)["users"] == [
        {
            'u_id': ef_u_id,
            'email': 'edward@gmail.com',
            'name_first': 'Edward',
            'name_last': 'Frankenstein',
            'handle_str': 'edwardfrankenstein'
        }
    ]

def test_users_all_access_three_users_at_once_in_order(make_user_ef, make_user_gh, make_user_ij):
    gh_token, gh_u_id = make_user_gh
    ef_token, ef_u_id = make_user_ef
    ij_token, ij_u_id = make_user_ij

    assert users_all(ij_token)["users"] == [
        {
            'u_id': gh_u_id,
            'email': 'gregory@gmail.com',
            'name_first': 'Gregory',
            'name_last': 'Heidelberg',
            'handle_str': 'gregoryheidelberg'
        }, 
        {
            'u_id': ef_u_id,
            'email': 'edward@gmail.com',
            'name_first': 'Edward',
            'name_last': 'Frankenstein',
            'handle_str': 'edwardfrankenstein'
        },
        {
            'u_id': ij_u_id,
            'email': 'ian@hotmail.com',
            'name_first': 'Ian',
            'name_last': 'Jacobs',
            'handle_str': 'ianjacobs'
        }
    ]

# register the users one at a time and access all the users
def test_users_all_register_and_call_function_one_at_a_time(make_user_ef, make_user_gh, make_user_ij):
    gh_token, gh_u_id = make_user_gh
    ef_token, ef_u_id = make_user_ef

    assert users_all(ef_token)["users"] == [
        {
            'u_id': gh_u_id,
            'email': 'gregory@gmail.com',
            'name_first': 'Gregory',
            'name_last': 'Heidelberg',
            'handle_str': 'gregoryheidelberg'
        }, 
        {
            'u_id': ef_u_id,
            'email': 'edward@gmail.com',
            'name_first': 'Edward',
            'name_last': 'Frankenstein',
            'handle_str': 'edwardfrankenstein'
        }
    ]

    ij_token, ij_u_id = make_user_ij
    assert users_all(ij_token)["users"] == [
        {
            'u_id': gh_u_id,
            'email': 'gregory@gmail.com',
            'name_first': 'Gregory',
            'name_last': 'Heidelberg',
            'handle_str': 'gregoryheidelberg'
        }, 
        {
            'u_id': ef_u_id,
            'email': 'edward@gmail.com',
            'name_first': 'Edward',
            'name_last': 'Frankenstein',
            'handle_str': 'edwardfrankenstein'
        },
        {
            'u_id': ij_u_id,
            'email': 'ian@hotmail.com',
            'name_first': 'Ian',
            'name_last': 'Jacobs',
            'handle_str': 'ianjacobs'
        }
    ]
    
def test_users_all_users_remain_when_logout(make_user_ef, make_user_gh, make_user_ij):
    gh_token, gh_u_id = make_user_gh
    ef_token, ef_u_id = make_user_ef
    ij_token, ij_u_id = make_user_ij
    auth_logout(ef_token)

    assert users_all(ij_token)["users"] == [
        {
            'u_id': gh_u_id,
            'email': 'gregory@gmail.com',
            'name_first': 'Gregory',
            'name_last': 'Heidelberg',
            'handle_str': 'gregoryheidelberg'
        }, 
        {
            'u_id': ef_u_id,
            'email': 'edward@gmail.com',
            'name_first': 'Edward',
            'name_last': 'Frankenstein',
            'handle_str': 'edwardfrankenstein'
        },
        {
            'u_id': ij_u_id,
            'email': 'ian@hotmail.com',
            'name_first': 'Ian',
            'name_last': 'Jacobs',
            'handle_str': 'ianjacobs'
        }
    ]

def test_users_all_invalid_token_error(make_user_ef):
    ef_token, ef_u_id = make_user_ef

    with pytest.raises(AccessError):
        users_all(ef_token + "invalid")

'''------------------testing search--------------------'''
# reminder
# input: (token, query_str); output: {messages}
# returns messages in ALL channels that user is in 
# TODO:
# add invalid token checks for all functions
# add @pytext_fixtures to all

# assume:
# 1. Search string no longer than 1000 characters long

# Search string tests: 
# testing that empty search string should return empty dictionary
def test_search_empty_string(create_public_channel):
    new_public_channel, user_ab = create_public_channel
    msg1 = message_send(user_ab['token'], new_public_channel['channel_id'], "Hello world!")

    assert search(user_ab['token'], "")['messages'] == []

# spaces in search string
def test_search_space_string(create_public_channel):
    new_public_channel, user_ab = create_public_channel
    msg1 = message_send(user_ab['token'], new_public_channel['channel_id'], "A message with spaces!")
    # result_list is of type list (list of dictionaries) 
    result_list = search(user_ab['token'], " ")['messages']
    
    assert result_list[0]['message_id'] == msg1['message_id']
    assert result_list[0]['u_id'] == user_ab['u_id']
    assert result_list[0]['message'] == "A message with spaces!"

# letters and symbols in search string (combination of above) 
def test_search_normal_string(create_public_channel): 
    pass

# search string longer than message (should be no match) 
def test_search_string_too_long(create_public_channel): 
    pass

# Cross-channel tests
# multiple matching messages in different channels a user is in
def test_search_string_in_multiple_channels(create_public_channel): 
    pass

# matching messages in unjoined channel shold not show up
def test_search_string_in_unjoined_channel(create_public_channel):
    pass

# Exceptions

# 1000 + long search string gives error
def test_search_invalid_string(create_public_channel):
    pass
    
# invalid token 
