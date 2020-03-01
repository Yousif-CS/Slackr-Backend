#please edit this file for channels functions
from auth import auth_login, auth_register
from channel import channel_messages, channel_leave, channel_join, addowner, removeowner, channel_invite, channel_details
from channels import channels_create
from message import message_send
import pytest

'''
    Under the assumption that auth_register, auth_login
    channels_create, channel_invite, message_send work properly
'''

'''------------------testing channel_messages--------------------'''

def test_channel_messages_empty_public(): 
   
    #creating user
    user_info = auth_register("Yousif@unsw.com", "13131", "Yousif", "Khalid")
    #creating public channel
    channel_id = channels_create(user_info['token'], 'test_channel0', True)    
    msgs = channel_messages(user_info['token'], channel_id['channel_id'], 0)
    assert(msgs['messages'] == [])
    assert(msgs['start'] == 0)
    assert(msgs['end'] == -1)

#testing whether it raises an exception given a start index > number of channel_messages
def test_channel_messages_empty_public_bad():
    #creating user
    user_info = auth_register("Yousif@unsw.com", "13131", "Yousif", "Khalid")
    #creating public channel
    channel_id = channels_create(user_info['token'], 'test_channel1', True)
    with pytest.raises(InputError):
        msgs = channel_messages(user_info['token'], channel_id['channel_id'], 10)

#testing accessing channel_messages as an non-member of the channel
def test_channel_messages_private_non_member():
    #creating and logging in users
    owner_info = auth_login("Yousif@unsw.com", "13131")
    user_info = auth_register("member@unsw.com","12321", "John", "Wick") 
    #creating private channel
    channel_id = channels_create(owner_info['token'], 'test_channel2', False)
    message_send(owner_info['token'], channel_id['channel_id'], "First Message!")
    with pytest.raises(AccessError):
         msgs = channel_messages(user_info['token'], channel_id['channel_id'], 0)

#testing obtaining channel_messages from an invalid channel
def test_channel_messages_invalid_channel():
    #creating and logging in users
    owner_info = auth_login("Yousif@unsw.com", "13131") 
    with pytest.raises(InputError):
        msgs = channel_messages(owner_info['token'], 131123, 0)

def test_channel_messages_invalid_index():
    #creating and logging in users
    owner_info = auth_login("Yousif@unsw.com", "13131")
    user_info = auth_login("member@unsw.com","12321", "John", "Wick") 
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel3', False)
    message_send(owner_info['token'], channel_id['channel_id'], "First Message!")
    message_send(owner_info['token'], channel_id['channel_id'], "Second Message!")
    message_send(owner_info['token'], channel_id['channel_id'], "Third Message!")
    with pytest.raises(InputError):
        msgs = channel_messages(user_info['token'], channel_id['channel_id'], 4)

def test_channel_messages_public_non_member():
    #logging in users
    owner_info = auth_login("Yousif@unsw.com", "13131")
    user_info = auth_login("member@unsw.com","12321", "John", "Wick") 
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel4', True)
    #message_sending channel_messages
    message_send(owner_info['token'], channel_id['channel_id'], "First Message!")
    #access channel_messages as a non-member to a public channel
     with pytest.raises(AccessError):
        msgs = channel_messages(user_info['token'], channel_id['channel_id'], 0)
        assert(msgs['end'] == -1)   #indicating the end of the channel_messages list

def test_channel_messages_unauthorized_user():
    #logging in users
    owner_info = auth_login("Yousif@unsw.com", "13131")
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel8', True)
    with pytest.raises(AccessError):
        msgs = channel_messages('I am an invalid token', channel_id['channel_id'], 0)

'''------------------testing channel_leave--------------------'''

#testing leaving an existing channel with a valid owner
def test_channel_leave_owner_good():
    #logging in users
    owner_info = auth_login("Yousif@unsw.com", "13131")
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel5', True)
    channel_leave(owner_info['token'], channel_id['channel_id'])
    #checking owner is not a member anymore
    with pytest.raises(AccessError):
        channel_details(owner_info['token'], channel_id['channel_id'])

#testing leaving a channel as a non-member
def test_channel_leave_non_member():
    #logging in users
    owner_info = auth_login("Yousif@unsw.com", "13131")
    user_info = auth_login("member@unsw.com","12321", "John", "Wick") 
    channel_list = channels.channels_list(owner_info['token'])
    channel5_id = [channel.get('channel_id') for channel in channel_list if channel.get('name') == 'test_channel5']
    with pytest.raises(AccessError):
        #I used an index 0 assuming that there is only one id for each channel name
        channel_leave(user_info['token'], channel5_id[0])
def test_channel_leave_invalid_channel_id():
    #logging in users
    owner_info = auth_login("Yousif@unsw.com", "13131")
    with pytest.raises(InputError):
        channel_leave(owner_info['token'], 1321231)

def test_channel_leave_general_member():
    #logging in users
    owner_info = auth_login("Yousif@unsw.com", "13131")
    user_info = auth_login("member@unsw.com","12321", "John", "Wick") 
    #creating a private channel
    channel_id = channels_create(owner_info['token'], 'test_channel6', False)
    channel_invite(owner_info['token'], channel_id['channel_id'], user_info['u_id'])
    channel_leave(user_info['token'], channel_id['channel_id'])
    #trying to access channel channel_details as a non-member
    with pytest.raises(AccessError):
        channel_details(user_info['token'], channel_id['channel_id'])

def test_channel_leave_unauthorized_user():
    #logging in users
    owner_info = auth_login("Yousif@unsw.com", "13131")
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel9', True)
    
    with pytest.raises(AccessError):
        channel_leave('I am an invalid token', channel_id['channel_id'])


'''------------------testing channel_join--------------------'''

#joining a valid channel with valid permissions
def test_join_public_valid():
    #logging in users
    owner_info = auth_login("Yousif@unsw.com", "13131")
    user_info = auth_login("member@unsw.com","12321", "John", "Wick") 
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel6', True)
    channel_join(user_info['token'], channel_id['channel_id'])
    #make sure user can view channel channel_details as member
    try:
        channel_details(user_info['token'], channel_id['channel_id'])
    except AccessError as exception
        assert (AccessError not exception)

#joining an invalid channel
def test_join_invalid_channel():
    #logging in users
    owner_info = auth_login("Yousif@unsw.com", "13131")
    with pytest.raises(InputError):
        channel_join(owner_info['token'], 1231212)

#joining a private channel as a general user(not an admin)
def test_join_private_member():
    #logging in users
    owner_info = auth_login("Yousif@unsw.com", "13131")
    user_info = auth_login("member@unsw.com","12321", "John", "Wick") 
    #creating a private channel
    channel_id = channels_create(owner_info['token'], 'test_channel6', False)
    with pytest.raises(AccessError):
        channel_join(user_info['token'], channel_id['channel_id'])
    
#joining a private channel as an admin
def test_join_private_admin():
    pass

#double joining a channel
def test_join_already_joined():
    #logging in users
    owner_info = auth_login("Yousif@unsw.com", "13131")
    user_info = auth_login("member@unsw.com","12321", "John", "Wick") 
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel6', True)
    channel_join(user_info['token'], channel_id['channel_id'])
    #Here I am assuming that double joining should raise any kind of exception
    with pytest.raises(Exception):
            channel_join(user_info['token'], channel_id['channel_id'])







