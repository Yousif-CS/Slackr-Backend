#please edit this file for channels functions
from auth import login, register
from channel import messages, leave, channel_join, addowner, removeowner
from channels import channel_create
from message import send
import pytest

'''
    Under the assumption that auth_register, auth_login
    channel_create, channel_invite, message_send work properly
'''
def test_messages_empty_public(): 
   
    #creating user
    user_info = register("Yousif@unsw.com", "13131", "Yousif", "Khalid")
    #creating public channel
    channel_id = channel_create(user_info['token'], 'test_channel0', True)    
    msgs = messages(user_info['token'], channel_id['channel_id'], 0)
    assert(msgs['messages'] == [])
    assert(msgs['start'] == 0)
    assert(msgs['end'] == -1)

#testing whether it raises an exception given a start index > number of messages
def test_messages_empty_public_bad():
    #creating user
    user_info = register("Yousif@unsw.com", "13131", "Yousif", "Khalid")
    #creating public channel
    channel_id = channel_create(user_info['token'], 'test_channel1', True)
    with pytest.raises(InputError):
        msgs = messages(user_info['token'], channel_id['channel_id'], 10)

#testing accessing messages as an non-member of the channel
def test_messages_private_non_member():
    #creating and logging in users
    owner_info = login("Yousif@unsw.com", "13131")
    user_info = register("member@unsw.com","12321", "John", "Wick") 
    #creating private channel
    channel_id = channel_create(owner_info['token'], 'test_channel2', False)
    send(owner_info['token'], channel_id['channel_id'], "First Message!")
    with pytest.raises(AccessError):
         msgs = messages(user_info['token'], channel_id['channel_id'], 0)

#testing obtaining messages from an invalid channel
def test_messages_invalid_channel():
    #creating and logging in users
    owner_info = login("Yousif@unsw.com", "13131") 
    with pytest.raises(InputError):
        msgs = messages(owner_info['token'], 131123, 0)

def test_messages_invalid_index():
    #creating and logging in users
    owner_info = login("Yousif@unsw.com", "13131")
    user_info = login("member@unsw.com","12321", "John", "Wick") 
    #creating a public channel
    channel_id = channel_create(owner_info['token'], 'test_channel3', False)
    send(owner_info['token'], channel_id['channel_id'], "First Message!")
    send(owner_info['token'], channel_id['channel_id'], "Second Message!")
    send(owner_info['token'], channel_id['channel_id'], "Third Message!")
    with pytest.raises(InputError):
        msgs = messages(user_info['token'], channel_id['channel_id'], 4)

def test_messages_public_non_member():
    #logging in users
    owner_info = login("Yousif@unsw.com", "13131")
    user_info = login("member@unsw.com","12321", "John", "Wick") 
    #creating a public channel
    channel_id = channel_create(owner_info['token'], 'test_channel4', True)
    #sending messages
    send(owner_info['token'], channel_id['channel_id'], "First Message!")
    #access messages as a non-member to a public channel
     with pytest.raises(AccessError):
        msgs = messages(user_info['token'], channel_id['channel_id'], 0)
        assert(msgs['end'] == -1)   #indicating the end of the messages list

'''------------------testing channel_leave--------------------'''

#testing leaving an existing channel with a valid owner
def test_leave_owner():
    #logging in users
    owner_info = login("Yousif@unsw.com", "13131")
#creating a public channel
    channel_id = channel_create(owner_info['token'], 'test_channel4', True)
    




