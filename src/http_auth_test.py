import time
from urllib.error import HTTPError
import pytest

from http_helpers import (reset, register, login, logout, channels_create, channel_join) 

def test_login_user(reset):
    reg_token = register('max.d@gmail.com', 'wubbalubba', 'Max', 'Smith')[1]
    login_token = login('max.d@gmail.com', 'wubbalubba')[1]

    assert reg_token == login_token 
    success = logout(login_token)
    assert success == True 


def test_login_multiple_users(reset):
    reg_token = register('max.d@gmail.com', 'wubbalubba', 'Max', 'Smith')[1]
    log_token = login('max.d@gmail.com', 'wubbalubba')[1]   
    logout(log_token)

    reg_token = register('bob@gmail.com', 'wubbalubba', 'Bob', 'Smith')[1]
    log_token = login('bob@gmail.com', 'wubbalubba')[1]
    logout(log_token)

    reg_token = register('mike@gmail.com', 'wubbalubba', 'Mike', 'Smith')[1]
    log_token = login('mike@gmail.com', 'wubbalubba')[1]
    logout(log_token)

def test_register_without_logging_out(reset):
    reg_token = register('max.d@gmail.com', 'wubbalubba', 'Max', 'Smith')[1]
    log_token = login('max.d@gmail.com', 'wubbalubba')[1]   
    assert log_token == reg_token 
    reg_token = register('max2.d@gmail.com', 'wubbalubba', 'Max', 'Smith')


def test_register_user_twice(reset):
    register('max.d@gmail.com', 'wubbalubba', 'Max', 'Smith')

    with pytest.raises(HTTPError):
        register('max.d@gmail.com', 'wubbalubba', 'Max', 'Smith')[1]


def test_login_non_user(reset):
    register('max.d@gmail.com', 'wubbalubba', 'Max', 'Smith')
    
    with pytest.raises(HTTPError):
        login('mike@gmail.com', 'wubbalubba')
    
def test_register_short_password(reset):
    with pytest.raises(HTTPError):
        register('max.d@gmail.com', 'wubba', 'Max', 'Smith')
    
def test_long_first_name(reset): 
    with pytest.raises(HTTPError):
        register('max.d@gmail.com', 'wubbalubba', 'a'* 51, 'Smith')

def test_long_last_name(reset):
    with pytest.raises(HTTPError):
        register('max.d@gmail.com', 'wubbalubba', 'Max', 'a'* 51)
    
def test_password_no_match(reset):
    register('max.d@gmail.com', 'wubbalubba', 'Max', 'Smith')
    
    with pytest.raises(HTTPError):
        login('max.d@gmail.com', 'wubbalub')

def test_invalid_email(reset):
    
    with pytest.raises(HTTPError):
        register('max.smith', 'wubbalubba', 'Max','Smith')
    
def test_join_channel_logged_out(reset):
    register('max.d@gmail.com', 'wubbalubba', 'Max', 'Smith')
    owner_token = login('max.d@gmail.com', 'wubbalubba')[1]
    channel_id = channels_create(owner_token, 'Maxs Channel', is_public=True)
    success = logout(owner_token)
    assert success == True 

    register('mike@gmail.com', 'wubbalubba', 'Mike', 'Smith')[1]
    user_token = login('mike@gmail.com', 'wubbalubba')[1]
    logout(user_token)

    with pytest.raises(HTTPError):
        channel_join(user_token, channel_id)
    