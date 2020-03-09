# please edit this file for channels functions
# TODO: write fixtures for creating channel, creating / registering users

import pytest
from channels import channels_list, channels_listall, channels_create
from error import InputError, AccessError
from channel import channel_invite, channel_details
from auth import auth_login, auth_register


'''------------------testing channels_list--------------------'''

# reminders
# input: (token); output: {channels}
# is_public status should not affect channnel

# testing whether channels_list returns empty list if no channels exist yet
def test_channels_list_no_channels(): 
    # creating and registering user (user_ab is type dictionary with u_id and token keys)
    user_ab = auth_register("alice@gmail.com", "password11", "Alice", "Bee")
    # assuming users are not part of any channel after registration
    # and that no channels have been created
    assert channels_list(user_ab['token'])['channels'] == []

# testing that channels_list returns a channel that the user created
def test_channels_list_creator_public_channel():
    # creating and registering users
    user_ab = auth_register("alice@gmail.com", "password11", "Alice", "Bee")
    user_cd = auth_register("charlie@gmail.com", "pw321ABC", "Charlie", "Dragon")
    # user_ab creates a public channel (new_public_channel is a dictionary with key channel_id)
    new_public_channel = channels_create(user_ab['token'], 'public_test_1', True)
    ab_list = channels_list(user_ab['token'])
    cd_list = channels_list(user_cd['token'])
    # assuming channel_id begins indexing from 1?
    assert ab_list['channels'] == [
        {
            'channel_id': new_public_channel['channel_id'], 
            'name': 'public_test_1'
        }
    ]
    assert cd_list['channels'] == []

# testing that private channels also shows up when channel_id is called by a user in channel
def test_channels_list_creator_private_channel():
    # creating and registering user
    user_ab = auth_register("alice@gmail.com", "password11", "Alice", "Bee")
    # user creates private channel
    new_private_channel = channels_create(user_ab['token'], 'private_test', False)
    ab_list = channels_list(user_ab['token'])
    assert ab_list['channels'] == \
        [
            {
                'channel_id': new_private_channel['channel_id'], 
                'name': 'private_test'
            }
        ]

# testing that channels_list also returns a channel if a user was added by the creator
def test_channels_list_added_by_creator():
    # creating and registering users
    user_ab = auth_register("alice@gmail.com", "password11", "Alice", "Bee")
    user_cd = auth_register("charlie@gmail.com", "pw321ABC", "Charlie", "Dragon")
    # user_ab creates a public channel
    new_channel = channels_create(user_ab['token'], 'test_add', True)
    # user_ab invites user_cd to the channel
    channel_invite(user_ab['token'], new_channel['channel_id'], user_cd['u_id'])
    #user_cd calls channels_list
    cd_list = channels_list(user_cd['token'])
    assert cd_list['channels'] == \
        [
            {
                'channel_id': new_channel['channel_id'], 
                'name': 'test_add'
            }
        ]

# testing that invalid token throws exception
# assuming token with string 'invalid' is an invalid token
def test_channels_list_invalid_token():
    user_ab = auth_register("alice@gmail.com", "password11", "Alice", "Bee")

    with pytest.raises(AccessError):
        ab_list = channels_list(user_ab["token"] + "invalid")

'''------------------testing channels_listall--------------------'''
# reminders
# input: (token); output: {channels}
# list every channel that exists (public and private)

# testing that channels_listall returns an empty dictionary when no channels exist
def test_channels_listall_empty():
    # creating and registering user_ab
    user_ab = auth_register("alice@gmail.com", "password11", "Alice", "Bee")
    # assuming users are not part of any channel after registration
    # and that no channels have been created
    assert channels_listall(user_ab['token'])['channels'] == []

# testing for a given public channel, channels_listall returns it for every user
def test_channels_listall_public(): 
    # creating and registering users
    user_ab = auth_register("alice@gmail.com", "password11", "Alice", "Bee")
    user_cd = auth_register("charlie@gmail.com", "pw321ABC", "Charlie", "Dragon")
    # user_ab creates a public channel
    new_public_channel = channels_create(user_ab['token'], 'public_test', True)
    new_public_channel2 = channels_create(user_cd['token'], 'public_test2', True)
    # user_ab and user_cd call channels_listall
    ab_list = channels_listall(user_ab['token'])['channels']
    cd_list = channels_listall(user_cd['token'])['channels']

    ab_lst_channel_ids = [ch["channel_id"] for ch in ab_list]
    cd_lst_channel_ids = [ch["channel_id"] for ch in cd_list]

    for id in ab_lst_channel_ids:
        assert id in cd_lst_channel_ids
    
    for id in cd_lst_channel_ids:
        assert id in ab_lst_channel_ids


# testing for a private channel, channels_listall also returns it for every user
def test_channels_listall_private():
    # creating and registering users
    user_ab = auth_register("alice@gmail.com", "password11", "Alice", "Bee")
    user_cd = auth_register("charlie@gmail.com", "pw321ABC", "Charlie", "Dragon")
    # user_cd creates a private channel
    new_private_channel = channels_create(user_ab['token'], 'private_test', False)
    new_private_channel2 = channels_create(user_cd['token'], 'private_test2', False)
    # user_ab and user_cd call channels_listall
    ab_list = channels_listall(user_ab['token'])['channels']
    cd_list = channels_listall(user_cd['token'])['channels']

    ab_lst_channel_ids = [ch["channel_id"] for ch in ab_list]
    cd_lst_channel_ids = [ch["channel_id"] for ch in cd_list]

    for id in ab_lst_channel_ids:
        assert id in cd_lst_channel_ids
    
    for id in cd_lst_channel_ids:
        assert id in ab_lst_channel_ids

# testing that invalid token throws exception
# assuming token with string 'invalid' is an invalid token
def test_channels_listall_invalid_token():
    user_ab = auth_register("alice@gmail.com", "password11", "Alice", "Bee")

    with pytest.raises(Exception):
        ab_listall = channels_listall(user_ab["token"] + "invalid")

'''------------------testing channels_create--------------------'''
# input: (token, name, is_public); output: {channel_id}
# throws InputError when name is more than 20 chars long
# assume: 
# 1. duplicate names allowed since IDs are different
# 2. NoName allowed ('name': '')

# testing for correct output (channel_id as int)
def test_channels_create_id_int():
    # creating and registering user
    user_kli = auth_register("ken@gmail.com", "new_pass", "Ken", "L")
    # creating a public channel
    new_channel_id = channels_create(user_kli['token'], "new_channel", True)
    assert isinstance(new_channel_id['channel_id'], int)

# testing for correct details (using channel_details)
def test_channels_create_correct_details():
    # creating and registering user
    user_kli = auth_register("ken@gmail.com", "new_pass", "Ken", "L")
    user_bwang = auth_register("bobw@gmail.com", "password123", "Bob", "Wang") 
    # creating a public channel
    new_channel_id = channels_create(user_kli['token'], "some_channel_name", True)
    # user_kli invites user_bwang to the channel
    channel_invite(user_kli['token'], new_channel_id['token'], user_bwang['u_id'])
    print_details = channel_details(user_kli['token'], new_channel_id['channel_id'])
    assert print_details['name'] == "some_channel_name"
    assert print_details['all_members'] == \
        [
            {'u_id': user_kli['u_id'], 'name_first': 'Ken', 'name_last': 'L'},
            {'u_id': user_bwang['u_id'], 'name_first': 'Bob', 'name_last': 'Wang'}
        ]

# testing that 2 different channels (maybe with same name) does not have same ID
def test_channels_create_unique_id():
    # creating and registering user
    user_kli = auth_register("ken@gmail.com", "new_pass", "Ken", "L")
    # creating 2 channels that have the same name and is_public status
    new_channel_1 = channels_create(user_kli['token'], "generic_name", True)
    new_channel_2 = channels_create(user_kli['token'], "generic_name", True)
    # checking for uniqueness of channel_id
    assert new_channel_1['channel_id'] != new_channel_2['channel_id']
    assert len(channels_listall(user_kli['token'])['channels']) == 2

# tests that channel whose name is exactly 20 characters long can be made
def test_channels_create_name_20char():
    user_kli = auth_register("ken@gmail.com", "new_pass", "Ken", "L")
    channels_create(user_kli['token'], "a" * 20, True)
    assert len(channels_listall(user_kli['token'])['channels']) == 1

# tests that a channel named with an empty string can be made
def test_channels_create_noname():
    user_kli = auth_register("ken@gmail.com", "new_pass", "Ken", "L")
    channels_create(user_kli['token'], "", True)
    assert len(channels_listall(user_kli['token'])['channels']) == 1

# testing for raised exception if len(name) > 20
def test_channels_create_invalid_name():
    # creating and registering user
    user_kli = auth_register("ken@gmail.com", "new_pass", "Ken", "L")
    with pytest.raises(InputError):
        bad_channel = channels_create(user_kli['token'], "verylongchannelnameamiat20charsyet", True)

# testing that invalid token throws exception
# assuming token with string 'invalid' is an invalid token
def test_channels_create_invalid_token():
    user_ab = auth_register("alice@gmail.com", "password11", "Alice", "Bee")

    with pytest.raises(Exception):
        invalid_channel = channels_create(user_ab['token'] + "invalid", "Invalid Token Channels suck", True)
