'''
This file contains tests for standup functions
'''
import standup
import pytest
import time
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


'''Testing standup_start'''
# 

'''Testing standup_active'''

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

def test_standup_active_active(create_public_channel):
    '''
    Testing calling the function with an active standup
    '''
    #creating a public channel
    channel_id, owner_info = create_public_channel
    #starting a standup
    time_finish = standup.standup_start(owner_info['token'], channel_id['channel_id'], 10)
    #getting the standup active status
    standup_details = standup.standup_active(owner_info['token'], channel_id['token'])
    #asserting
    assert standup_details['is_active'] is True
    assert standup_details['time_finish'] == time_finish

def test_standup_active_finished(create_public_channel):
    '''
    Testing calling the function after a standup has ended
    '''
    #creating a public channel
    channel_id, owner_info = create_public_channel
    #starting a standup
    time_finish = standup.standup_start(owner_info['token'], channel_id['channel_id'], 3)
    time.sleep(4)   #sleep for 4 seconds
    #getting the standup active status
    standup_details = standup.standup_active(owner_info['token'], channel_id['token'])
    #asserting
    assert standup_details['is_active'] is False
    assert standup_details['time_finish'] is None

def test_standup_active_invalid_token(create_public_channel):
    '''
    Testing using an invalid token while calling the function -> accessError
    '''
    #creating a public channel
    channel_id, owner_info = create_public_channel
    #starting a standup
    with pytest.raises(AccessError):
        standup_details = standup.standup_active(owner_info['token'] + str(1), channel_id['token'])


'''Testing standup_send'''

def test_standup_send_invalid_channel(create_public_channel):
    '''
    Testing calling the function with an invalid channel_id
    '''
    #creating a public channel
    channel_id, owner_info = create_public_channel
    #starting a standup
    time_finish = standup.standup_start(owner_info['token'], channel_id['channel_id'], 3)
    #sending a message to a standup
    with pytest.raises(InputError):
        standup.standup_send(owner_info['token'], channel_id['channel_id'] + 1, "My standup!")

def test_standup_send_no_active_standup(create_public_channel):
    '''
    Testing sending a message to a non-existent standup
    '''
    #creating a public channel
    channel_id, owner_info = create_public_channel
    with pytest.raises(InputError):
        standup.standup_send(owner_info['token'], channel_id['channel_id'], "My first standup!")


def test_standup_send_finished_standup(create_public_channel):
    '''
    Testing sending a message to an already finished standup
    '''
    #creating a public channel
    channel_id, owner_info = create_public_channel
    #start a standup
    time_finish = standup.standup_start(owner_info['token'], channel_id['channel_id'], 3)
    #sleep for a bit
    time.sleep(5)
    with pytest.raises(InputError):
        standup.standup_send(owner_info['token'], channel_id['channel_id'], "My first standup!")

def test_standup_send_long_message(create_public_channel):
    '''
    Testing sending a very long message ( > 1000) results in an exception
    '''
    #creating a public channel
    channel_id, owner_info = create_public_channel
    #start a standup
    time_finish = standup.standup_start(owner_info['token'], channel_id['channel_id'], 3)
    #sending
    with pytest.raises(InputError):
        standup.standup_send(owner_info['token'], channel_id['channel_id'], "a" * 1001)
    
def test_standup_send_non_member(create_public_channel, create_user1):
    '''
    Testing trying to send to a channel's standup that we do not belong to
    '''
    #creating a public channel
    channel_id, owner_info = create_public_channel
    #creating a general user
    user_info = create_user1
    #creating a standup
    time_finish = standup.standup_start(owner_info['token'], channel_id['channel_id'], 3)
    #sending
    with pytest.raises(AccessError):
        standup.standup_send(user_info['token'], channel_id['channel_id'], "Intruder!")


def test_standup_send_empty_message(create_public_channel):
    '''
    Testing trying to send an empty message to a standup ignores the message
    '''
    #creating a public channel
    channel_id, owner_info = create_public_channel
    #creating a standup
    time_finish = standup.standup_start(owner_info['token'], channel_id['channel_id'], 3)
    #sending
    with pytest.raises(InputError):
        standup.standup_send(owner_info['token'], channel_id['channel_id'], "")


def test_standup_send_invalid_token(create_public_channel):
    '''
    Testing using an invalid token while calling the function -> accessError
    '''
    #creating a public channel
    channel_id, owner_info = create_public_channel
    #starting a standup
    with pytest.raises(AccessError):
        standup.standup_send(owner_info['token'] + str(1), channel_id['token'], "Aaaahhh!")


