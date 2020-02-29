#please edit this file for channels functions
from auth import login, register
from channel import messages, leave, channel_join, addowner, removeowner, invite, details
from channels import channel_create
from message import send
import pytest

'''
    Under the assumption that auth_register, auth_login
    channel_create, channel_invite, message_send work properly
'''

'''------------------testing channel_messages--------------------'''

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

def test_messages_unauthorized_user():
    #logging in users
    owner_info = login("Yousif@unsw.com", "13131")
    #creating a public channel
    channel_id = channel_create(owner_info['token'], 'test_channel8', True)
    with pytest.raises(AccessError):
        msgs = messages('I am an invalid token', channel_id['channel_id'], 0)

'''------------------testing channel_leave--------------------'''

#testing leaving an existing channel with a valid owner
def test_leave_owner_good():
    #logging in users
    owner_info = login("Yousif@unsw.com", "13131")
    #creating a public channel
    channel_id = channel_create(owner_info['token'], 'test_channel5', True)
    leave(owner_info['token'], channel_id['channel_id'])
    #checking owner is not a member anymore
    with pytest.raises(AccessError):
        channel_details(owner_info['token'], channel_id['channel_id'])

#testing leaving a channel as a non-member
def test_leave_non_member():
    #logging in users
    owner_info = login("Yousif@unsw.com", "13131")
    user_info = login("member@unsw.com","12321", "John", "Wick") 
    channel_list = channels.list(owner_info['token'])
    channel5_id = [channel.get('channel_id') for channel in channel_list if channel.get('name') == 'test_channel5']
    with pytest.raises(AccessError):
        #I used an index 0 assuming that there is only one id for each channel name
        leave(user_info['token'], channel5_id[0])
def test_leave_invalid_channel_id():
    #logging in users
    owner_info = login("Yousif@unsw.com", "13131")
    with pytest.raises(InputError):
        leave(owner_info['token'], 1321231)

def test_leave_general_member():
    #logging in users
    owner_info = login("Yousif@unsw.com", "13131")
    user_info = login("member@unsw.com","12321", "John", "Wick") 
    #creating a private channel
    channel_id = channel_create(owner_info['token'], 'test_channel6', False)
    invite(owner_info['token'], channel_id['channel_id'], user_info['u_id'])
    leave(user_info['token'], channel_id['channel_id'])
    #trying to access channel details as a non-member
    with pytest.raises(AccessError):
        details(user_info['token'], channel_id['channel_id'])

def test_leave_unauthorized_user():
    #logging in users
    owner_info = login("Yousif@unsw.com", "13131")
    #creating a public channel
    channel_id = channel_create(owner_info['token'], 'test_channel9', True)
    
    with pytest.raises(AccessError):
        leave('I am an invalid token', channel_id['channel_id'])


'''------------------testing channel_join--------------------'''

#joining a valid channel with valid permissions
def test_join_public_valid():
    #logging in users
    owner_info = login("Yousif@unsw.com", "13131")
    user_info = login("member@unsw.com","12321", "John", "Wick") 
    #creating a public channel
    channel_id = channel_create(owner_info['token'], 'test_channel6', True)
    channel_join(user_info['token'], channel_id['channel_id'])
    #make sure user can view channel details as member
    try:
        details(user_info['token'], channel_id['channel_id'])
    except AccessError as exception
        assert (AccessError not exception)

#joining an invalid channel
def test_join_invalid_channel():
    #logging in users
    owner_info = login("Yousif@unsw.com", "13131")
    with pytest.raises(InputError):
        channel_join(owner_info['token'], 1231212)

#joining a private channel as a general user(not an admin)
def test_join_private_member():
    #logging in users
    owner_info = login("Yousif@unsw.com", "13131")
    user_info = login("member@unsw.com","12321", "John", "Wick") 
    #creating a private channel
    channel_id = channel_create(owner_info['token'], 'test_channel6', False)
    with pytest.raises(AccessError):
        channel_join(user_info['token'], channel_id['channel_id'])
    
#joining a private channel as an admin
def test_join_private_admin():
    pass

#double joining a channel
def test_join_already_joined():
    #logging in users
    owner_info = login("Yousif@unsw.com", "13131")
    user_info = login("member@unsw.com","12321", "John", "Wick") 
    #creating a public channel
    channel_id = channel_create(owner_info['token'], 'test_channel6', True)
    channel_join(user_info['token'], channel_id['channel_id'])
    #Here I am assuming that double joining should raise any kind of exception
    with pytest.raises(Exception):
            channel_join(user_info['token'], channel_id['channel_id'])






