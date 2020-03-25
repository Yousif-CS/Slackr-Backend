#please edit this file for channels functions
from auth import auth_login, auth_register
from channel import channel_leave, channel_join, channel_addowner, channel_removeowner, channel_invite, channel_messages, channel_details
from channels import channels_create, channels_list
from message import message_send, message_remove
from error import AccessError, InputError
from other import workspace_reset
import pytest

from server import get_store
'''
    Under the assumption that auth_register, auth_login
    channels_create, channel_invite, message_send, message_remove work properly
'''

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
    channel_id = channels_create(owner_info['token'], 'test_channel', True)    
    return (channel_id, owner_info)

@pytest.fixture
def create_private_channel(create_owner):
    '''
    Create a private channel using the owner fixture and return their details
    '''
    owner_info = create_owner
    channel_id = channels_create(owner_info['token'], 'test_channel', False)    
    return (channel_id, owner_info)


''' -------------------------testing channel_invite -------------------------------- '''


def test_channel_invite_valid(create_user1, create_public_channel):
    ''' 
    testing owner of a channel can invite a registered user
    '''
    #reseting the state of the server
    workspace_reset()
    user_info = create_user1 
    channel_id, owner_info = create_public_channel 	

    channel_invite(owner_info['token'], channel_id['channel_id'], user_info['u_id'])
    all_membs = channel_details(owner_info['token'], channel_id['channel_id'])['all_members']
    u_ids = [member['u_id'] for member in all_membs]
    assert user_info['u_id'] in u_ids
    assert len(all_membs) == 2

def test_channel_user_invite(create_user1, create_user2, create_public_channel):
    ''' 
    testing if user can invite another user to a channel they belong to 
    '''
    #reseting the state of the server
    workspace_reset()
    #creating channel and users
    inviting_user_info = create_user1 
    user_invited_info = create_user2
    channel_id, owner_info = create_public_channel	

    #inviting users
    channel_invite(owner_info['token'], channel_id['channel_id'], inviting_user_info['u_id'])
    channel_invite(inviting_user_info['token'], channel_id['channel_id'], user_invited_info['u_id'])

    #getting channel details
    ch_details = channel_details(owner_info['token'], channel_id['channel_id'])['all_members']
    u_ids = [member['u_id'] for member in ch_details]

    assert owner_info['u_id'] in u_ids
    assert inviting_user_info['u_id'] in u_ids
    assert user_invited_info in u_ids

def test_channel_invite_non_user(create_public_channel):
    '''
	Inviting a user id that doesn't belong to any registered user to a channel
	'''
    #reseting the state of the server
    workspace_reset()
    channel_id, owner_info = create_public_channel
    rand_user_id = owner_info['u_id'] + 1 

    with pytest.raises(InputError):
        channel_invite(owner_info['token'], channel_id['channel_id'], rand_user_id)


def test_channel_invite_user_as_non_member(create_user1, create_user2,  create_public_channel): 
    '''
    Produces an input error when a user invites another registered user to a channel they don't belong to
	'''
    #reseting the state of the server
    workspace_reset()
    user_info = create_user1 
    invited_user = create_user2
    channel_id, owner_info = create_public_channel 	

    with pytest.raises(AccessError):
    	channel_invite(user_info['token'], channel_id['channel_id'], invited_user['u_id'] )


def test_channel_double_invite(create_user1, create_public_channel):
    '''
    Input Error occurs when same member is invited to a channel they are already belong to
    '''
    #reseting the state of the server
    workspace_reset()

    #Creating users and channel
    user_info = create_user1 
    channel_id, owner_info = create_public_channel	

    #inviting one user 
    channel_invite(owner_info['token'], channel_id['channel_id'], user_info['u_id'])

    #double inviting
    with pytest.raises(InputError): 
        channel_invite(owner_info['token'], channel_id['channel_id'], user_info['u_id'])

def test_channel_invite_nonexistent_channel(create_public_channel, create_user1):

    #reseting the state of the server
    workspace_reset()

    channel_id, owner_info = create_public_channel
    user_info = create_user1

    with pytest.raises(InputError):
        channel_invite(owner_info["token"], channel_id["channel_id"] + 1, user_info["u_id"])

''' -------------------Testing channel_details -----------------'''

def test_channel_details__owners_valid(create_public_channel, create_user1, create_user2): 
    '''
    Test channel_details gives correct info about owners
    '''	
    #reseting the state of the server
    workspace_reset()

    #creating users and channel
    new_ch, owner_info = create_public_channel 
    user_info = create_user1
    user2_info = create_user2

    #joining channel
    channel_invite(owner_info["token"], new_ch["channel_id"], user_info["u_id"])
    channel_join(user2_info["token"], new_ch["channel_id"])

    #getting channel details
    details = channel_details(owner_info['token'], new_ch['channel_id'])
    owners = details['owner_members']
    owners_ids = [owner['u_id'] for owner in owners]

    assert owner_info['u_id'] in owners_ids
    assert len(owners) == 1

def test_channel_details_members_valid(create_public_channel, create_user1, create_user2):
    '''
    Test channel_details gives correct info about members
    '''	
    #reseting the state of the server
    workspace_reset()

    #creating channel and members
    new_ch, owner_info = create_public_channel 
    user_info = create_user1
    user2_info = create_user2

    #joining the channel
    channel_invite(owner_info["token"], new_ch["channel_id"], user_info["u_id"])
    channel_join(user2_info["token"], new_ch["channel_id"])

    #getting channel details
    details = channel_details(user_info['token'], new_ch['channel_id'])
    all_membs = details['all_members'] 
    members_ids = [member['u_id'] for member in all_membs]

    #testing if details are correct regarding members
    assert user_info['u_id'] in members_ids
    assert user2_info['u_id'] in members_ids
    assert owner_info['u_id'] in members_ids
    assert len(all_membs) == 3

def test_channel_details_name_valid(create_public_channel):
    '''
    Test channel_details gives correct channel name
    '''
    #reseting the state of the server
    workspace_reset()

    #creating channel and members
    new_ch, owner_info = create_public_channel 

    #getting channel details
    details = channel_details(owner_info['token'], new_ch['channel_id'])
    channel_name = details['name'] 

    assert channels_list(owner_info["token"])["channels"][0]["name"] == channel_name



def test_channel_details_no_id(create_private_channel):
    '''
    Input error when channel_id does not exist
    '''
    #reseting the state of the server
    workspace_reset()

    channel_id, owner_info = create_private_channel 

    non_channel_id = channel_id['channel_id'] + 1 

    with pytest.raises(InputError): 
        channel_details(owner_info['token'], non_channel_id) 

def test_channel_details_non_member(create_user1, create_public_channel):
    ''' 
    Access Error occurs when a user that does not belong to a channel attempts to retrieve its details 
    ''' 
    #reseting the state of the server
    workspace_reset()

    channel_id, owner_info = create_public_channel 
    user_info = create_user1  

    with pytest.raises(AccessError): 
        channel_details(user_info['token'], channel_id['channel_id']) 

def test_channel_details_invalid_token(create_public_channel, create_user1):
    '''
    Access Error occurs when an unauthorized  user invokes the function
    '''
    #reseting the state of the server
    workspace_reset()

    channel_id, owner_info = create_public_channel 
    with pytest.raises(AccessError): 
        channel_details("I am an invalid token", channel_id['channel_id']) 

'''------------------testing channel_messages--------------------'''
def test_channel_messages_good(create_public_channel):
    '''
    General test to add 5 messages and checking returned dictionary
    '''
    #reseting the state of the server
    workspace_reset()

    #create a public channel using fixture and return its details and the owner's
    channel_id, owner_info = create_public_channel
    #sending messages
    sent_msgs_ids = []
    sent_msgs_ids.append(message_send(owner_info['token'], channel_id['channel_id'], "message 1"))
    sent_msgs_ids.append(message_send(owner_info['token'], channel_id['channel_id'], "message 2"))
    sent_msgs_ids.append(message_send(owner_info['token'], channel_id['channel_id'], "message 3"))
    sent_msgs_ids.append(message_send(owner_info['token'], channel_id['channel_id'], "message 4"))
    sent_msgs_ids.append(message_send(owner_info['token'], channel_id['channel_id'], "message 5"))
    #retrieving message list
    msgs = channel_messages(owner_info['token'], channel_id['channel_id'], 0)
    assert len(msgs['messages']) == 5
    assert msgs['start'] == 0
    assert msgs['end'] == -1
    u_ids = [message['u_id'] for message in msgs['messages']]
    retrieved_msgs_ids = [message['message_id'] for message in msgs['messages']]
    for user in u_ids:
        assert user == owner_info['u_id']
    #testing if the returned ids of the messages are the same as the sent ids of the messages
    for sent_msg, ret_msg in zip(sent_msgs_ids, retrieved_msgs_ids):
        assert sent_msg == ret_msg 

def test_channel_messages_more_than_fifty(create_public_channel):
    '''
    Testing sending more than 50 messages and checking the function returns only the first 50 (pagination)
    Unfortunately, we have to use a for loop
    '''
    #reseting the state of the server
    workspace_reset()

    print(get_store())
    #create a public channel using fixture and return its details and the owner's
    channel_id, owner_info = create_public_channel
    sent_msgs_ids = []
    #for loop to send messages
    for i in range(51):
        sent_msgs_ids.append(message_send(owner_info['token'], channel_id['channel_id'], "message " + str(i)))

    #retrieving message list
    msgs = channel_messages(owner_info['token'], channel_id['channel_id'], 0)

    #asserting start and end are correct
    assert msgs['start'] == 0
    assert msgs['end'] == 50

    #changing the start message to 1
    msgs1 = channel_messages(owner_info['token'], channel_id['channel_id'], 1)

    #asserting start and end are correct
    assert msgs['start'] == 1
    assert msgs['end'] == -1

def test_channel_messages_empty_public(create_public_channel): 
    '''
    Testing requesting messages from an empty channel using a bad start index (0)
    '''
    #reseting the state of the server
    workspace_reset()

    #create a public channel using fixture and return its details and the owner's
    channel_id, owner_info = create_public_channel
    with pytest.raises(InputError):
        channel_messages(owner_info['token'], channel_id['channel_id'], 0)
    
def test_channel_messages_empty_public_bad(create_public_channel):
    '''
    testing whether it raises an exception given a start index > number of channel_messages
    '''
    #reseting the state of the server
    workspace_reset()

    #create a public channel using fixture and return its details and the owner's
    channel_id, owner_info = create_public_channel
    with pytest.raises(InputError):
        msgs = channel_messages(owner_info['token'], channel_id['channel_id'], 10)

def test_channel_messages_private_non_member(create_private_channel, create_user1):
    '''
    testing accessing channel_messages as an non-member of the channel
    '''
    #reseting the state of the server
    workspace_reset()

    #creating channel and retrieving its details and the owner's
    channel_id, owner_info = create_private_channel
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
    #reseting the state of the server
    workspace_reset()

    #creating and logging in owner
    owner_info = create_owner 
    with pytest.raises(InputError):
        msgs = channel_messages(owner_info['token'], 131123, 0)


def test_channel_messages_invalid_index(create_public_channel):
    '''
    Another test to check exception throwing while giving invalid start index
    '''
    #reseting the state of the server
    workspace_reset()

    #creating channel and retrieving its details and the owner's
    channel_id, owner_info = create_public_channel
    #sending messages
    message_send(owner_info['token'], channel_id['channel_id'], "First Message!")
    message_send(owner_info['token'], channel_id['channel_id'], "Second Message!")
    message_send(owner_info['token'], channel_id['channel_id'], "Third Message!")
    with pytest.raises(InputError):
        msgs = channel_messages(owner_info['token'], channel_id['channel_id'], 4)

def test_channel_messages_public_non_member(create_public_channel, create_user1):
    '''
    Testing a non-member access to channel_messages
    '''
    #reseting the state of the server
    workspace_reset()

    #creating channel and retrieving its details and the owner's
    channel_id, owner_info = create_public_channel
    #creating general user
    user_info = create_user1
    #message_sending channel_messages
    msg_id = message_send(owner_info['token'], channel_id['channel_id'], "First Message!")
    #access channel_messages as a non-member to a public channel
    with pytest.raises(AccessError):
        msgs = channel_messages(user_info['token'], channel_id['channel_id'], 0)

def test_channel_messages_public_member(create_public_channel, create_user1):
    '''
    Testing member access to channel_messages
    '''
    #reseting the state of the server
    workspace_reset()

    channel_id, owner_info = create_public_channel
    user_info = create_user1
    channel_join(user_info["token"], channel_id["channel_id"])
    msg_id = message_send(user_info['token'], channel_id['channel_id'], "First Message!")

    assert channel_messages(user_info["token"], channel_id["channel_id"], 0)["messages"][0]["message"] == \
        "First Message!"
        
def test_channel_messages_unauthorized_user(create_public_channel):
    '''
    Testing unauthorized access(not a member of slackr) to channel_messages
    '''
    #reseting the state of the server
    workspace_reset()

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
    #reseting the state of the server
    workspace_reset()

    #creating channel and retrieving its details and the owner's
    channel_id, owner_info = create_public_channel
    #leaving channel
    channel_leave(owner_info['token'], channel_id['channel_id'])
    #checking owner is not a member anymore
    with pytest.raises(AccessError):
        channel_details(owner_info['token'], channel_id['channel_id'])

def test_channel_leave_correct_details(create_private_channel, create_user1):
    '''
    Testing channel is actually updated if user leaves by using channel_details
    '''
    #reseting the state of the server
    workspace_reset()

    #creating user and channel
    new_ch, owner_info = create_private_channel
    user_info = create_user1

    #inviting user
    channel_invite(owner_info["token"], new_ch["channel_id"], user_info["u_id"])

    #getting details
    all_membs = channel_details(owner_info['token'], new_ch['channel_id'])['all_members']
    u_ids = [member['u_id'] for member in all_membs]

    #asserting user is in the channel
    assert user_info['u_id'] in u_ids
    assert len(all_membs) == 2

    channel_leave(user_info["token"], new_ch["channel_id"])

    #getting details
    all_membs = channel_details(owner_info['token'], new_ch['channel_id'])['all_members']
    u_ids = [member['u_id'] for member in all_membs]
    assert user_info['u_id'] not in u_ids
    assert len(all_membs) == 1

def test_channel_leave_owner_private(create_private_channel):
    '''
    testing leaving an existing private channel as the owner. This is to test if 
    it is okay since the private channel would have no members that can invite people later on
    '''
    #reseting the state of the server
    workspace_reset()

    #creating channel and retrieving its details and the owner's
    channel_id, owner_info = create_private_channel

    #checking owner is not a member anymore
    with pytest.raises(Exception):
        #leaving channel
        channel_leave(owner_info['token'], channel_id['channel_id'])


def test_channel_leave_non_member(create_public_channel, create_user1):
    '''
    Testing leaving a channel as a non-member
    '''
    #reseting the state of the server
    workspace_reset()

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
    #reseting the state of the server
    workspace_reset()

    owner_info = create_owner
    with pytest.raises(InputError):
        channel_leave(owner_info['token'], 1321231)

def test_channel_leave_general_member(create_private_channel, create_user1):
    '''
    Testing leaving a channel as a general member and trying to access its details
    '''
    #reseting the state of the server
    workspace_reset()

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
    #reseting the state of the server
    workspace_reset()

    channel_id, owner_info = create_public_channel
    #assuming an invalid token results in an exception
    with pytest.raises(Exception):
        channel_leave('I am an invalid token', channel_id['channel_id'])


'''------------------testing channel_join--------------------'''

def test_channel_join_public_valid(create_public_channel, create_user1):
    '''
    Join a channel with valid conditions
    '''
    #reseting the state of the server
    workspace_reset()

    #creating a public channel
    channel_id, owner_info = create_public_channel
    #creating a normal user
    user_info = create_user1
    #joining as general user
    channel_join(user_info['token'], channel_id['channel_id'])
    #make sure user can view channel channel_details as member
    try:
        test_details = channel_details(user_info['token'], channel_id['channel_id'])
        assert test_details #asserting it is not empty
        assert test_details['name'] == 'test_channel' 
    except AccessError:
        assert False


def test_channel_join_invalid_channel(create_owner):
    '''
    Joining an invalid channel
    '''
    #reseting the state of the server
    workspace_reset()

    #logging in users
    owner_info = create_owner
    with pytest.raises(InputError):
        channel_join(owner_info['token'], 1231212)

def test_channel_join_private_member(create_private_channel, create_user1):
    '''
    joining a private channel as a general user(not an admin)
    '''
    #reseting the state of the server
    workspace_reset()

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
    #reseting the state of the server
    workspace_reset()

    #creating a public channel
    channel_id, owner_info = create_public_channel
    #creating a normal user and joining
    user_info = create_user1
    channel_join(user_info['token'], channel_id['channel_id'])
    #Here I am assuming that double joining should raise any kind of exception
    with pytest.raises(Exception):
            channel_join(user_info['token'], channel_id['channel_id'])

def test_channel_join_invalid_token(create_public_channel):
    '''
    Providing an invalid token
    '''
    #reseting the state of the server
    workspace_reset()

    #creating a public channel
    channel_id, owner_info = create_public_channel
    #testing using an invalid token raises an exception
    with pytest.raises(Exception):
        channel_join('I am not a valid token', channel_id['channel_id'])

'''------------------testing channel_addowner--------------------'''


def test_channel_addowner_good(create_public_channel, create_user1):
    '''
    Testing adding an owner, and allowing them to delete a message by another user
    '''
    #reseting the state of the server
    workspace_reset()

    #creating a public channel
    channel_id, owner_info = create_public_channel
    #creating a normal user
    user_info = create_user1
    #sending a message that we will test deleting afterwards
    msg_id = message_send(owner_info['token'], channel_id['channel_id'], "Owner1's Message!")
    #adding general user as an owner to the channel
    channel_addowner(owner_info['token'], channel_id['channel_id'], user_info['u_id'])
    #trying to remove a message as a new owner; if it fails, addowner is buggy
    try:
        message_remove(user_info['token'], msg_id['message_id'])
    except AccessError:
        assert False

def test_channel_addowner_invalid_channel(create_owner, create_user1):
    '''
    Under the assumption that 22222 is an invalid channel id
    '''
    #reseting the state of the server
    workspace_reset()

    #logging in users
    owner_info = create_owner
    user_info = create_user1
    with pytest.raises(InputError):
        #adding general user as an owner to an invalid channel
        channel_addowner(owner_info['token'],22222, user_info['u_id'])

def test_channel_addowner_again(create_public_channel, create_user1):
    '''
    Testing double adding
    '''
    #reseting the state of the server
    workspace_reset()

    #creating a public channel
    channel_id, owner_info = create_public_channel
    #creating a normal user
    user_info = create_user1
    #adding general user as an owner to the channel
    channel_addowner(owner_info['token'], channel_id['channel_id'], user_info['u_id'])
    with pytest.raises(InputError):
        #adding owner again
        channel_addowner(owner_info['token'], channel_id['channel_id'], user_info['u_id'])

def test_channel_addowner_as_non_owner(create_public_channel, create_user1, create_user2):
    '''
    being a general member, trying to add a user as an owner
    '''
    #reseting the state of the server
    workspace_reset()

    #creating a public channel
    channel_id, owner_info = create_public_channel
    #creating a normal user
    user_info = create_user1
    another_user = create_user2
    #joining as a general member and trying to add another user as an owner
    channel_join(another_user['token'], channel_id['channel_id'])
    with pytest.raises(AccessError):
        channel_addowner(another_user['token'], channel_id['channel_id'], user_info['u_id'])

def test_channel_addowner_as_non_member(create_public_channel, create_user1, create_user2):
    '''
    Testing adding a user as an owner as a non-member
    '''
    #reseting the state of the server
    workspace_reset()

    #creating a public channel
    channel_id, owner_info = create_public_channel
    #creating normal users
    user_info = create_user1
    channel_join(user_info['token'], channel_id['channel_id'])
    another_user = create_user2
    #trying to make a user an owner as a non member
    with pytest.raises(Exception):
        channel_addowner(another_user['token'], channel_id['channel_id'], user_info['u_id'])

def test_channel_addowner_invalid_token(create_public_channel, create_user1):
    '''
    Unauthorized user trying to add a member as an owner
    '''
    #reseting the state of the server
    workspace_reset()

    #creating a public channel
    channel_id, owner_info = create_public_channel
    #creating normal users
    user_info = create_user1
    channel_join(user_info['token'], channel_id['channel_id'])
    #testing using an invalid token raises an exception
    with pytest.raises(Exception):
        channel_addowner('I am not a valid token', channel_id['channel_id'], user_info['u_id'])

'''------------------testing channel_removeowner--------------------'''

def test_channel_removeowner_good(create_public_channel, create_user1):
    '''
    Assuming addowner works fine, we test removing a message after ownership is removed
    '''
    #reseting the state of the server
    workspace_reset()

    #creating a public channel
    channel_id, owner_info = create_public_channel
    #creating normal users
    user_info = create_user1
    #sending a message that we will test deleting afterwards
    msg_id = message_send(owner_info['token'], channel_id['channel_id'], "First owner's Message 1!")
    msg_id2 = message_send(owner_info['token'], channel_id['channel_id'], "First owner's  Message 2!")
    #adding general user as an owner to the channel
    channel_addowner(owner_info['token'], channel_id['channel_id'], user_info['u_id'])
    #trying to remove a message to check if addowner works
    message_remove(user_info['token'], msg_id2['message_id'])
    messages = channel_messages(owner_info['token'], channel_id['channel_id'], 0)
    assert len(messages['messages']) == 1
    #removing user from being an owner
    channel_removeowner(owner_info['token'], channel_id['channel_id'], user_info['u_id'])
    #trying to remove a message as a user, it should produce AccessError
    with pytest.raises(AccessError):
        message_remove(user_info['token'], msg_id['message_id'])

def test_channel_removeowner_invalid_channel(create_public_channel, create_user1):
    '''
    Assuming 22222 is an invalid channel id
    '''
    #reseting the state of the server
    workspace_reset()

    #creating a public channel
    channel_id, owner_info = create_public_channel
    #creating normal users
    user_info = create_user1
    channel_addowner(owner_info['token'], channel_id['channel_id'], user_info['u_id'])
    with pytest.raises(InputError):
        #removing a user from an invalid channel
        channel_removeowner(owner_info['token'],22222, user_info['u_id'])

def test_channel_removeowner_no_owner(create_public_channel, create_user1):
    '''
    trying to remove ownership from a user who is not an owner
    '''
    #reseting the state of the server
    workspace_reset()

    #creating a public channel
    channel_id, owner_info = create_public_channel
    #creating normal users
    user_info = create_user1

    with pytest.raises(InputError):
        #removing a user from an invalid channel
        channel_removeowner(owner_info['token'],channel_id['channel_id'], user_info['u_id'])

def test_channel_removeowner_as_non_owner(create_public_channel, create_user1):
    '''
    Removing an owner as a general member
    '''
    #reseting the state of the server
    workspace_reset()

    #creating a public channel
    channel_id, owner_info = create_public_channel
    #creating normal users
    user_info = create_user1
    #joining as a general member and trying to removing another user as an owner
    channel_join(user_info['token'], channel_id['channel_id'])
    with pytest.raises(AccessError):
        channel_removeowner(user_info['token'], channel_id['channel_id'], owner_info['u_id'])

def test_channel_removeowner_as_non_member(create_public_channel, create_user1):
    '''
    Removing an owner without a member of the channel
    '''
    #reseting the state of the server
    workspace_reset()

    #creating a public channel
    channel_id, owner_info = create_public_channel
    #creating normal users
    user_info = create_user1
    #trying to make a remove a user as a non member
    with pytest.raises(Exception):
        channel_removeowner(user_info['token'], channel_id['channel_id'], owner_info['u_id'])

def test_channel_removeowner_invalid_token(create_public_channel):
    '''
    Removing an owner as an unauthorized user
    '''
    #reseting the state of the server
    workspace_reset()

    #creating a public channel
    channel_id, owner_info = create_public_channel
    #testing using an invalid token raises an exception
    with pytest.raises(AccessError):
        channel_removeowner('I am not a valid token', channel_id['channel_id'], owner_info['u_id'])