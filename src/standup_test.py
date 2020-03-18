'''
This file contains tests for standup functions
'''
import standup
import pytest
from auth import auth_login, auth_register
from channels import channels_create
from error import InputError, AccessError
from datetime import datetime

'''Fixtures to be used in testing'''

@pytest.fixture
def create_owner():
    '''
    Just a fixture to register an owner and return its details
    '''
    user_info = auth_register("Yousif@gmail.com", "13131ABC", "Yousif", "Khalid")
    return user_info

@pytest.fixture
def create_user1():
    '''
    Create a general user and return its details
    '''
    user_info = auth_register("member@gmail.com", "12321AB", "John", "Wick")
    return user_info

@pytest.fixture
def create_user2():
    '''
    Create a general user and return its details
    '''
    user_info = auth_register("holaAmigos@gmail.com", "123A456!", "Banana", "Guy")
    return user_info

@pytest.fixture
def create_public_channel():
    '''
    Create a public channel using the owner fixture and return their details
    '''
    owner_info = auth_register("Yousif@gmail.com", "13131ABC", "Yousif", "Khalid")
    channel_id = channels_create(owner_info['token'], 'test_channel', True)
    return (channel_id, owner_info)

@pytest.fixture
def create_private_channel():
    '''
    Create a private channel using the owner fixture and return their details
    '''
    owner_info = auth_register("Yousif@gmail.com", "13131ABC", "Yousif", "Khalid")
    channel_id = channels_create(owner_info['token'], 'test_channel', False)   
    return (channel_id, owner_info)


def test_standup_active_invalid_channel(create_public_channel):
    '''
    Testing whether the function throws an exception given an invalid channel_id
    '''
    #creating a public channel
    channel_id, owner_info = create_public_channel
    #testing an invalid channel id produces an exception
    with pytest.raises(InputError):
        standup.standup_active(owner_info['token'], channel_id['channel_id'] + 1)

def test_standup_active_inactive(create_public_channel):
    '''
    Testing calling the function with no active standup
    '''
    #creating a public channel
    channel_id, owner_info = create_public_channel
    #getting the details
    standup_details = standup.standup_active(owner_info['token'], channel_id['channel_id'])
    assert standup_details['is_active'] is False
    assert standup_details['time_finished'] is None

def test_standup_active_active():
    