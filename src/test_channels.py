# please edit this file for channels functions
# TODO: import functions from other modules if needed
# register users for each individual test function
import pytest
import channels
from error import InputError
from channel import channel_invite
from auth import auth_login, auth_register


# creating users
# need to re-create users from scratch for each test

# creating and registering users
user_ab = auth_register("alice@gmail.com", "password11", "Alice", "Bee")
user_cd = auth_register("charlie@gmail.com", "pw321ABC", "Charlie", "Dragon")

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
    assert channels_list(user_ab['token']) == {}

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
    assert ab_list['channels'] == \
        [
            {
                'channel_id': 1
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
                'channel_id': 1
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
                'channel_id': new_channel['channel_id']
                'name': 'test_add'
            }
        ]

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
    assert channels_listall(user_ab['token']) == {}

# testing for a given public channel, channels_listall returns it for every user
def test_channels_listall_public(): 
    # creating and registering users
    user_ab = auth_register("alice@gmail.com", "password11", "Alice", "Bee")
    user_cd = auth_register("charlie@gmail.com", "pw321ABC", "Charlie", "Dragon")
    # user_ab creates a public channel
    new_public_channel = channels_create(user_ab['token'], 'public_test', True)
    # user_ab and user_cd call channels_listall
    ab_list = channels_list(user_ab['token'])
    cd_list = channels_list(user_cd['token'])
    assert ab_list['channels'] == cd_list['channels'] == \
        [
            {
                'channel_id': 1
                'name': 'public_test'
            }
        ]


# testing for a private channel, channels_listall also returns it for every user
def test_channels_listall_private():
    # creating and registering users
    user_ab = auth_register("alice@gmail.com", "password11", "Alice", "Bee")
    user_cd = auth_register("charlie@gmail.com", "pw321ABC", "Charlie", "Dragon")
    # user_cd creates a private channel
    new_private_channel = channels_create(user_ab['token'], 'private_test', False)
    # user_ab and user_cd call channels_listall
    ab_list = channels_list(user_ab['token'])
    cd_list = channels_list(user_cd['token'])
    assert cd_list['channels'] == ab_list['channels'] == \
        [
            {
                'channel_id': 1
                'name': 'private_test'
            }
        ]

'''------------------testing channels_create--------------------'''