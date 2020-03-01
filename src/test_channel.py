#please edit this file for channels functions
from auth import auth_login, auth_register
from channel import channel_messages, channel_leave, channel_join, channel_addowner, channel_removeowner, channel_invite, channel_details
from channels import channels_create, channels_list
from message import message_send, message_remove
from error import AccessError, InputError
import pytest

'''
    Under the assumption that auth_register, auth_login
    channels_create, channel_invite, message_send, message_remove work properly
'''

'''------------------testing channel_messages--------------------'''

def test_channel_messages_empty_public(): 
    #creating user
    user_info = auth_register("Yousif@gmail.com", "13131ABC", "Yousif", "Khalid")
    #creating public channel
    channel_id = channels_create(user_info['token'], 'test_channel0', True)    
    msgs = channel_messages(user_info['token'], channel_id['channel_id'], 0)
    #here I assume that the channel is empty once it is created(no messages)
    assert msgs['messages'] == []
    assert msgs['start'] == 0
    assert msgs['end'] == -1

#testing whether it raises an exception given a start index > number of channel_messages
def test_channel_messages_empty_public_bad():
    #creating user
    user_info = auth_register("Yousif@gmail.com", "13131ABC", "Yousif", "Khalid")
    #creating public channel
    channel_id = channels_create(user_info['token'], 'test_channel1', True)
    with pytest.raises(InputError):
        msgs = channel_messages(user_info['token'], channel_id['channel_id'], 10)

#testing accessing channel_messages as an non-member of the channel
def test_channel_messages_private_non_member():
    #creating and logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_register("member@gmail.com","12321AB", "John", "Wick") 
    #creating private channel
    channel_id = channels_create(owner_info['token'], 'test_channel2', False)
    message_send(owner_info['token'], channel_id['channel_id'], "First Message!")
    with pytest.raises(AccessError):
         msgs = channel_messages(user_info['token'], channel_id['channel_id'], 0)

#testing obtaining channel_messages from an invalid channel
def test_channel_messages_invalid_channel():
    #creating and logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC") 
    with pytest.raises(InputError):
        msgs = channel_messages(owner_info['token'], 131123, 0)

def test_channel_messages_invalid_index():
    #creating and logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB") 
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel3', False)
    message_send(owner_info['token'], channel_id['channel_id'], "First Message!")
    message_send(owner_info['token'], channel_id['channel_id'], "Second Message!")
    message_send(owner_info['token'], channel_id['channel_id'], "Third Message!")
    with pytest.raises(InputError):
        msgs = channel_messages(user_info['token'], channel_id['channel_id'], 4)

def test_channel_messages_public_non_member():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB") 
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel4', True)
    #message_sending channel_messages
    msg_id = message_send(owner_info['token'], channel_id['channel_id'], "First Message!")
    #access channel_messages as a non-member to a public channel
    with pytest.raises(AccessError):
        msgs = channel_messages(user_info['token'], channel_id['channel_id'], 0)
        assert msgs['end'] == -1   #indicating the end of the channel_messages list
        assert msg_id['message_id'] in [message.get('message_id') for message in msgs['messages']]

def test_channel_messages_unauthorized_user():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel8', True)
    with pytest.raises(AccessError):
        msgs = channel_messages('I am an invalid token', channel_id['channel_id'], 0)

'''------------------testing channel_leave--------------------'''

#testing leaving an existing channel with a valid owner
def test_channel_leave_owner_good():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel5', True)
    channel_leave(owner_info['token'], channel_id['channel_id'])
    #checking owner is not a member anymore
    with pytest.raises(AccessError):
        channel_details(owner_info['token'], channel_id['channel_id'])

#testing leaving a channel as a non-member
def test_channel_leave_non_member():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB") 
    channel_list = channels_list(owner_info['token'])
    channel5_id = [channel.get('channel_id') for channel in channel_list['channels'] if channel.get('name') == 'test_channel5']
    with pytest.raises(AccessError):
        #under the assumption that channels created in previous tests still exist
        assert channel5_id #making sure channel5_id is not empty
        #I used an index 0 assuming that there is only one id for each channel name
        channel_leave(user_info['token'], channel5_id[0])
def test_channel_leave_invalid_channel_id():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    with pytest.raises(InputError):
        channel_leave(owner_info['token'], 1321231)

def test_channel_leave_general_member():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB") 
    #creating a private channel
    channel_id = channels_create(owner_info['token'], 'test_channel6', False)
    channel_invite(owner_info['token'], channel_id['channel_id'], user_info['u_id'])
    channel_leave(user_info['token'], channel_id['channel_id'])
    #trying to access channel channel_details as a non-member
    with pytest.raises(AccessError):
        channel_details(user_info['token'], channel_id['channel_id'])

def test_channel_leave_unauthorized_user():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel9', True)
    #assuming an invalid token results in an exception
    with pytest.raises(Exception):
        channel_leave('I am an invalid token', channel_id['channel_id'])


'''------------------testing channel_join--------------------'''

#joining a valid channel with valid permissions
def test_join_public_valid():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB") 
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel6', True)
    channel_join(user_info['token'], channel_id['channel_id'])
    #make sure user can view channel channel_details as member
    try:
        test_details = channel_details(user_info['token'], channel_id['channel_id'])
        assert test_details != None
        assert test_details['name'] == 'test_channel6' 
    except AccessError as exception:
        assert AccessError != exception

#joining an invalid channel
def test_join_invalid_channel():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    with pytest.raises(InputError):
        channel_join(owner_info['token'], 1231212)

#joining a private channel as a general user(not an admin)
def test_join_private_member():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB") 
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
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB") 
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel6', True)
    channel_join(user_info['token'], channel_id['channel_id'])
    #Here I am assuming that double joining should raise any kind of exception
    with pytest.raises(Exception):
            channel_join(user_info['token'], channel_id['channel_id'])


'''------------------testing channel_addowner--------------------'''


def test_channel_addowner_good():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB") 
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel11', True)    
    #sending a message that we will test deleting afterwards
    msg_id = message_send(owner_info['token'], channel_id['channel_id'], "Owner1's Message!")
    #adding general user as an owner to the channel
    channel_addowner(owner_info['token'], channel_id['channel_id'], user_info['u_id'])
    #trying to remove a message as a new owner; if it fails, addowner is buggy
    try:
        message_remove(user_info['token'], msg_id['message_id'])
    except AccessError as exception:
        assert AccessError != exception

def test_channel_addowner_invalid_channel():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB")
    with pytest.raises(InputError):
        #adding general user as an owner to the channel
        channel_addowner(owner_info['token'],22222, user_info['u_id'])

def test_channel_addowner_again():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB") 
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel12', True)
    #adding general user as an owner to the channel
    channel_addowner(owner_info['token'], channel_id['channel_id'], user_info['u_id'])
    with pytest.raises(InputError):
        #adding owner again
        channel_addowner(owner_info['token'], channel_id['channel_id'], user_info['u_id'])

def test_channel_addowner_as_non_owner():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB") 
    another_user = auth_register("holaAmigos@gmail.com", "123A456!", "Banana", "Guy")
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel13', True)
    #joining as a general member and trying to add another user as an owner
    channel_join(another_user['token'], channel_id['channel_id'])
    with pytest.raises(AccessError):
        channel_addowner(another_user['token'], channel_id['channel_id'], user_info['u_id'])
    
def test_channel_addowner_as_non_member():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB") 
    another_user = auth_login("holaAmigos@gmail.com", "123A456!")
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel14', True)
    #trying to make a user an owner as a non member
    with pytest.raises(Exception):
        channel_addowner(another_user['token'], channel_id['channel_id'], user_info['u_id'])

def test_channel_addowner_invalid_token():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB")
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel14', True)
    #testing using an invalid token raises an exception
    with pytest.raises(Exception):
        channel_addowner('I am not a valid token', channel_id['channel_id'], user_info['u_id'])

'''------------------testing channel_removeowner--------------------'''
