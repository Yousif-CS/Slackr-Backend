#please edit this file for channels functions
from auth import auth_login, auth_register
from channel import channel_leave, channel_join, channel_addowner, channel_removeowner, channel_invite, channel_messages, channel_details
from channels import channels_create, channels_list
from message import message_send, message_remove
from error import AccessError, InputError
import pytest

'''
    Under the assumption that auth_register, auth_login
    channels_create, channel_invite, message_send, message_remove work properly
'''

'''------------------testing channel_messages--------------------'''
@pytest.fixture
def create_owner():
    '''
    Just a fixture to register an owner and return its details
    '''
    user_info = auth_register("Yousif@gmail.com", "13131ABC", "Yousif", "Khalid")
    return user_info

@pytest.fixture
def create_user1()
    '''
    Create a general user and return its details
    '''
    user_info = auth_register("member@gmail.com","12321AB", "John", "Wick") 
    return user_info

@pytest.fixture
def create_user2():
    '''
    Create a general user and return its details
    '''
    user_info = auth_register("holaAmigos@gmail.com", "123A456!", "Banana", "Guy")
    return user_info

@pytest.fixture
def create_public_channel(create_owner):
    '''
    Create a public channel using the owner fixture and return their details
    '''
    owner_info = create_owner
    channel_id = channels_create(user_info['token'], 'test_channel', True)    
    return (channel_id, owner_info)

@pytest.fixture
def create_private_channel(create_owner):
    '''
    Create a private channel using the owner fixture and return their details
    '''
    owner_info = create_owner
    channel_id = channels_create(owner_info['token'], 'test_channel', False)    
    return (channel_id, owner_info)


def test_channel_messages_empty_public(create_public_channel): 
    '''
    Testing requesting messages from an empty channel using a correct start index (0)
    '''
    #create a public channel using fixture and return its details and the owner's
    channel_id, owner_info = create_public_channel
    msgs = channel_messages(owner_info['token'], channel_id['channel_id'], 0)
    #here I assume that the channel is empty once it is created(no messages)
    assert msgs['messages'] == []
    assert msgs['start'] == 0
    assert msgs['end'] == -1

def test_channel_messages_empty_public_bad(create_public_channel):
    '''
    testing whether it raises an exception given a start index > number of channel_messages
    '''
    #create a public channel using fixture and return its details and the owner's
    channel_id, owner_info = create_public_channel
    with pytest.raises(InputError):
        msgs = channel_messages(user_info['token'], channel_id['channel_id'], 10)

def test_channel_messages_private_non_member(create_private_channel, create_user1):
    '''
    testing accessing channel_messages as an non-member of the channel
    '''
    #creating channel and retrieving its details and the owner's
    channel_id, owner_info = create_public_channel
    #creating a general user
    user_info = create_user1
    #creating private channel
    channel_id = channels_create(owner_info['token'], 'test_channel2', False)
    message_send(owner_info['token'], channel_id['channel_id'], "First Message!")
    with pytest.raises(AccessError):
         msgs = channel_messages(user_info['token'], channel_id['channel_id'], 0)


def test_channel_messages_invalid_channel(create_owner):
    '''
    testing obtaining channel_messages from an invalid channel
    '''
    #creating and logging in owner
    owner_info = create_owner 
    with pytest.raises(InputError):
        msgs = channel_messages(owner_info['token'], 131123, 0)


def test_channel_messages_invalid_index(create_public_channel):
    '''
    Another test to check exception throwing while giving invalid start index
    '''
    
    #creating channel and retrieving its details and the owner's
    channel_id, owner_info = create_public_channel
    #sending messages
    message_send(owner_info['token'], channel_id['channel_id'], "First Message!")
    message_send(owner_info['token'], channel_id['channel_id'], "Second Message!")
    message_send(owner_info['token'], channel_id['channel_id'], "Third Message!")
    with pytest.raises(InputError):
        msgs = channel_messages(user_info['token'], channel_id['channel_id'], 4)

def test_channel_messages_public_non_member(create_public_channel, create_user1):
    '''
    Testing a non-member access to channel_messages
    '''
    #creating channel and retrieving its details and the owner's
    channel_id, owner_info = create_public_channel
    #creating general user
    user_info = create_user1
    #message_sending channel_messages
    msg_id = message_send(owner_info['token'], channel_id['channel_id'], "First Message!")
    #access channel_messages as a non-member to a public channel
    with pytest.raises(AccessError):
        msgs = channel_messages(user_info['token'], channel_id['channel_id'], 0)
        

def test_channel_messages_unauthorized_user(create_public_channel):
    '''
    Testing unauthorized access(not a member of slackr) to channel_messages
    '''
    #creating channel and retrieving its details and the owner's
    channel_id, owner_info = create_public_channel
    #using an invalid token
    with pytest.raises(AccessError):
        msgs = channel_messages('I am an invalid token', channel_id['channel_id'], 0)

'''------------------testing channel_leave--------------------'''


def test_channel_leave_owner_good(create_public_channel):
    '''
    testing leaving an existing channel with a valid owner
    '''
    #creating channel and retrieving its details and the owner's
    channel_id, owner_info = create_public_channel
    #leaving channel
    channel_leave(owner_info['token'], channel_id['channel_id'])
    #checking owner is not a member anymore
    with pytest.raises(AccessError):
        channel_details(owner_info['token'], channel_id['channel_id'])


def test_channel_leave_non_member(create_public_channel, create_user1):
    '''
    Testing leaving a channel as a non-member
    '''
    #creating channel and retrieving its details and the owner's
    channel_id, owner_info = create_public_channel
    #creating another user
    user_info = create_user1
    #leaving as a non-member
    with pytest.raises(AccessError):
        channel_leave(user_info['token'], channel_id['channel_id'])

def test_channel_leave_invalid_channel_id(create_owner):
    '''
    Assuming 1321231 is not a valid channel id 
    '''
    owner_info = create_owner
    with pytest.raises(InputError):
        channel_leave(owner_info['token'], 1321231)

def test_channel_leave_general_member(create_private_channel, create_user1):
    '''
    Testing leaving a channel as a general member and trying to access its details
    '''
    #creating a private channel
    channel_id, owner_info = create_private_channel
    #creating a normal user
    user_info = create_user1
    #inviting a user
    channel_invite(owner_info['token'], channel_id['channel_id'], user_info['u_id'])
    #leaving
    channel_leave(user_info['token'], channel_id['channel_id'])
    #trying to access channel_details as a non-member
    with pytest.raises(AccessError):
        channel_details(user_info['token'], channel_id['channel_id'])

def test_channel_leave_unauthorized_user(create_public_channel):
    '''
    Testing leaving a channel as a user with an invalid token
    '''
    channel_id, owner_info = create_public_channel
    #assuming an invalid token results in an exception
    with pytest.raises(Exception):
        channel_leave('I am an invalid token', channel_id['channel_id'])


'''------------------testing channel_join--------------------'''

def test_channel_join_public_valid(create_public_channel, create_user1):
    '''
    Join a channel with valid conditions
    '''
    #creating a public channel
    channel_id, owner_info = create_public_channel
    #creating a normal user
    user_info = create_user1
    #joining as general user
    channel_join(user_info['token'], channel_id['channel_id'])
    #make sure user can view channel channel_details as member
    try:
        test_details = channel_details(user_info['token'], channel_id['channel_id'])
        assert test_details
        assert test_details['name'] == 'test_channel' 
    except AccessError as exception:
        assert AccessError != exception


def test_channel_join_invalid_channel(create_owner):
    '''
    Joining an invalid channel
    '''
    #logging in users
    owner_info = create_owner
    with pytest.raises(InputError):
        channel_join(owner_info['token'], 1231212)

def test_channel_join_private_member():
    '''
    joining a private channel as a general user(not an admin)
    '''
    #creating a private channel
    channel_id, owner_info = create_private_channel
    #creating a normal user
    user_info = create_user1

    with pytest.raises(AccessError):
        channel_join(user_info['token'], channel_id['channel_id'])
    
#joining a private channel as an admin
#def test_channel_join_private_admin():
#    pass

def test_channel_join_already_joined(create_public_channel, create_user1):
    '''
    Testing double joining a channel
    '''
    #creating a public channel
    channel_id, owner_info = create_public_channel
    #creating a normal user and joining
    user_info = create_user1
    channel_join(user_info['token'], channel_id['channel_id'])
    #Here I am assuming that double joining should raise any kind of exception
    with pytest.raises(Exception):
            channel_join(user_info['token'], channel_id['channel_id'])

def test_channel_join_invalid_token(create_public_channel):
    #creating a public channel
    channel_id, owner_info = create_public_channel
    #testing using an invalid token raises an exception
    with pytest.raises(Exception):
        channel_join('I am not a valid token', channel_id['channel_id'])

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

def test_channel_removeowner_good():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB") 
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel15', True)    
    #sending a message that we will test deleting afterwards
    msg_id = message_send(owner_info['token'], channel_id['channel_id'], "Owner1's Message!")
    #adding general user as an owner to the channel
    channel_addowner(owner_info['token'], channel_id['channel_id'], user_info['u_id'])
    #removing user from being an owner
    channel_removeowner(owner_info['token'], channel_id['channel_id'], user_info['u_id'])
    #trying to remove a message as a user, it should produce AccessError
    with pytest.raises(AccessError):
        message_remove(user_info['token'], msg_id['message_id'])

def test_channel_removeowner_invalid_channel():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB")
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel16', True)
    channel_addowner(owner_info['token'], channel_id['channel_id'], user_info['u_id'])
    with pytest.raises(InputError):
        #removing a user from an invalid channel
        channel_removeowner(owner_info['token'],22222, user_info['u_id'])

#trying to remove ownership from a user who is not an owner
def test_channel_removeowner_no_owner():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB")
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel17', True)
    with pytest.raises(InputError):
        #removing a user from an invalid channel
        channel_removeowner(owner_info['token'],channel_id['channel_id'], user_info['u_id'])

def test_channel_removeowner_as_non_owner():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB") 
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel21', True)
    #joining as a general member and trying to removing another user as an owner
    channel_join(user_info['token'], channel_id['channel_id'])
    with pytest.raises(AccessError):
        channel_removeowner(user_info['token'], channel_id['channel_id'], owner_info['u_id'])
    
def test_channel_removeowner_as_non_member():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB") 
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel20', True)
    #trying to make a remove a user as a non member
    with pytest.raises(Exception):
        channel_removeowner(user_info['token'], channel_id['channel_id'], owner_info['u_id'])

def test_channel_removeowner_invalid_token():
    #logging in users
    owner_info = auth_login("Yousif@gmail.com", "13131ABC")
    user_info = auth_login("member@gmail.com","12321AB")
    #creating a public channel
    channel_id = channels_create(owner_info['token'], 'test_channel19', True)
    #testing using an invalid token raises an exception
    with pytest.raises(Exception):
        channel_removeowner('I am not a valid token', channel_id['channel_id'], user_info['u_id'])
