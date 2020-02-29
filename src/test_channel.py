#please edit this file for channels functions
from auth import login, register
from channel import messages, leave, channel_join, addowner, removeowner
from channels import channel_create
from message import send
import pytest
def test_messages_empty_public(): 
    '''
    Under the assumption that auth_register, auth_login
    channel_create, message_send work properly
    '''
    #creating user
    user_info = register("Yousif@unsw.com", "13131", "Yousif", "Khalid")
    #creating public channel
    channel_id = channel_create(user_info['token'], 'test_channel', True)    
    msgs = messages(user_info['token'], channel_id['channel_id'], 0)
    assert(msgs['messages'] == [])
    assert(msgs['start'] == 0)
    assert(msgs['end'] == -1)

#testing whether it raises an exception given a start index > number of messages
def test_messages_empty_public_bad():
    #creating user
    user_info = register("Yousif@unsw.com", "13131", "Yousif", "Khalid")
    #creating public channel
    channel_id = channel_create(user_info['token'], 'test_channel', True)
    with pytest.raises(InputError):
        msgs = messages(user_info['token'], channel_id['channel_id'], 10)

#testing accessing messages as an non-member of the channel
def test_messages_private_owner():
    #creating and logging in users
    owner_info = login("Yousif@unsw.com", "13131")
    user_info = register("member@unsw.com","12321", "John", "Wick") 
    #creating private channel
    channel_id = channel_create(owner_info['token'], 'private_channel1', False)
    send(owner_info['token'], channel_id['channel_id'], "First Message!")
    with pytest.raises(AccessError):
         msgs = messages(user_info['token'], channel_id['channel_id'], 0)

#testing obtaining messages from an invalid channel
def test_messages_invalid_channel():
    #creating and logging in users
    owner_info = login("Yousif@unsw.com", "13131") 
    with pytest.raises(InputError):
        msgs = messages(owner_info['token'], 131123, 0)