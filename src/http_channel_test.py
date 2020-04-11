'''
Using urllib module to test channel functions (check http_helpers.py)
'''
# pylint: disable=unused-import
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=trailing-whitespace
# pylint: disable=missing-function-docstring
# pylint: disable=mixed-indentation
import time
from math import isclose
from urllib.error import HTTPError
import pytest

from http_helpers import (reset, register, login, logout,
                          message_send, channel_invite, channel_details, channels_create,
                          channel_messages, channel_join, channel_leave,
                          channel_addowner, channel_removeowner,
                          message_remove, channels_list)

MESSAGE_BLOCK = 50

#Testing channel_invite 

def test_channel_invite_public_ok(reset):
    '''
    Test inviting a user to a public channel places that user immediately in the channel
    '''
    _, owner_token = register('max.d@gmail.com', 'wubbalubba', 'Max', 'Smith')
    user_id, user_token = register('bob@gmail.com', 'wubbalubba', 'Bob', 'Smith')
    channel_id = channels_create(owner_token, 'Maxs Channel', is_public=True)

    channel_invite(owner_token, channel_id, user_id)
    all_membs = channel_details(user_token, channel_id)[2]
    u_ids = [member['u_id'] for member in all_membs]

    assert user_id in u_ids
    

def test_channel_invite_private_ok(reset):
    '''
    Test inviting a user to a public channel places that user immediately in the channel
    '''
    _, owner_token = register('max.d@gmail.com', 'wubbalubba', 'Max', 'Smith')
    user_id, user_token = register('bob@gmail.com', 'wubbalubba', 'Bob', 'Smith')
    channel_id = channels_create(owner_token, 'Maxs Channel', is_public=False)

    channel_invite(owner_token, channel_id, user_id)
    all_membs = channel_details(user_token, channel_id)[2]
    u_ids = [member['u_id'] for member in all_membs]

    assert user_id in u_ids
    
def test_channel_invite_no_u_id(reset):
    ''' 
	Test inviting an invalid user id raises an HTTP error
	'''
    owner_token = register('max.d@gmail.com', 'wubbalubba', 'Max', 'Smith')[1]
    channel_id = channels_create(owner_token, 'Maxs Channel', is_public=False)
    user_id = register('max.d.s@gmail.com', 'wubbalubba', 'Max', 'Smith')[0]

    rand_id = user_id + 1 
    with pytest.raises(HTTPError):
	    channel_invite(owner_token, channel_id, rand_id)
	

def test_channel_invite_as_non_member(reset):
	''' 
	Testing inviting a user to a channel using an invalid token 
	'''

	owner_token = register('max.d@gmail.com', 'wubbalubba', 'Max', 'Smith')[1]
	channel_id = channels_create(owner_token, 'Maxs Channel', is_public=False)
	user_id = register('max.d.s@gmail.com', 'wubbalubba', 'Max', 'Smith')[0]
	rand_token = owner_token + 'a'

	with pytest.raises(HTTPError):
		channel_invite(rand_token, channel_id, user_id)
	

def test_channel_invite_no_channel_id(reset):
	''' 
	Testing inviting a user to a channel with an invalid channel_id 
	'''

	owner_token = register('max.d@gmail.com', 'wubbalubba', 'Max', 'Smith')[1]
	channel_id = channels_create(owner_token, 'Maxs Channel', is_public=False)
	user_id = register('max.d.s@gmail.com', 'wubbalubba', 'Max', 'Smith')[0]
	rand_channel_id = channel_id + 1
	with pytest.raises(HTTPError):
		channel_invite(owner_token, rand_channel_id, user_id)

# Testing channel_details 

def test_channel_details_correct_info(reset):
	''' 
	Test channel_details provides correct information regarding 
    a channel's name, its owner members, and all of its members
	'''

	owner_id, owner_token = register('max.d@gmail.com', 'wubbalubba', 'Max', 'Smith')
	user_id, user_token = register('bob@gmail.com', 'wubbalubba', 'Bob', 'Smith')
	channel_id = channels_create(owner_token, 'Maxs Channel', is_public=False)

	channel_invite(owner_token, channel_id, user_id)
 
	name, owner_membs, all_membs = channel_details(user_token, channel_id)
	members_ids = [member['u_id'] for member in all_membs]
	owners_ids = [owner['u_id'] for owner in owner_membs]

	assert user_id in members_ids
	assert owner_id in members_ids 
	assert len(all_membs) == 2

	assert owner_id in owners_ids
	assert len(owner_membs) == 1

	assert name == 'Maxs Channel'

def test_channel_details_no_channel_id(reset):
	''' 
	Testing channel_details raises an exception when an invalid channel_id is given
	'''

	owner_token = register('max.d@gmail.com', 'wubbalubba', 'Max', 'Smith')[1]
	channel_id = channels_create(owner_token, 'Maxs Channel', is_public=False)
	rand_channel_id = channel_id + 1

	with pytest.raises(HTTPError):
		channel_details(owner_token, rand_channel_id)

def	test_channel_details_not_a_member(reset):
	'''
	Testing channel_details raises an exception 
    when a non-member of a channel tries to retrieve its details
	'''
	
	owner_token = register('max.d@gmail.com', 'wubbalubba', 'Max', 'Smith')[1]
	channel_id = channels_create(owner_token, 'Maxs Channel', is_public=False)
	new_user_token = register('bob@gmail.com', 'wubbalubba', 'Bob', 'Smith')[1]

	with pytest.raises(HTTPError):
		channel_details(new_user_token, channel_id)


# Testing channel_messages

def test_channel_messages_out_of_range(reset):
    '''
    Testing providing start_index that is out of range
    '''
    # register
    my_token = register(
        'z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    # create a channel
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)

    with pytest.raises(HTTPError):
        channel_messages(my_token, channel_id, start=1)

def test_channel_messages_one_message(reset):
    '''
    Testing getting a list containing one message
    '''
    # register
    my_uid, my_token = register(
        'z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')
    # create a channel
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    # send a message
    msg_id = message_send(my_token, channel_id, 'first message!')
    time_created = time.time()
    # get the messages
    messages, start, end = channel_messages(my_token, channel_id, start=0)
    # asserting
    assert messages[0]['message'] == 'first message!'
    assert messages[0]['message_id'] == msg_id
    assert messages[0]['u_id'] == my_uid
    assert isclose(time_created, messages[0]['time_created'], abs_tol=1)
    assert messages[0]['reacts'][0]['u_ids'] == []
    assert start == 0
    assert end == -1
    # logging out as next test requires logging in
    logout(my_token)


def test_channel_messages_two_messages():
    '''
    Testing sending another message to the server WITHOUT resetting
    '''
    my_token = login('z5236259@unsw.edu.au', '1231FFF!')[1]

    # getting the available channel and sending a message
    channel_id = channels_list(my_token)[0]['channel_id']
    msg_id = message_send(my_token, channel_id, 'second message!')
    time_created = time.time()
    # getting the messages
    messages, start, end = channel_messages(my_token, channel_id, start=0)
    # asserting
    assert messages[0]['message'] == 'second message!'
    assert messages[0]['message_id'] == msg_id
    assert isclose(time_created, messages[0]['time_created'], abs_tol=1)
    assert messages[1]['message'] == 'first message!'
    assert start == 0
    assert end == -1


def test_channel_messages_more_than_fifty(reset):
    '''
    Testing sending over 50 messages and requesting the first 50
    '''
    my_token = register('z5236259@unsw.edu.au',
                        '1231FFF!', 'Yousif', 'Khalid')[1]
    # create a channel
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    # sending the messages
    for i in range(51):
        message_send(my_token, channel_id, f"message {i}")
    # getting the messages
    messages, start, end = channel_messages(my_token, channel_id, start=0)
    # asserting
    assert len(messages) == MESSAGE_BLOCK
    assert messages[0]['message'] == 'message 50'  # last message sent
    assert messages[-1]['message'] == 'message 1'  # oldest message sent
    assert start == 0
    assert end == MESSAGE_BLOCK


def test_channel_messages_invalid_channel_id(reset):
    '''
    Testing calling the route with an invalid channel id
    '''
    my_token = register('z5236259@unsw.edu.au',
                        '1231FFF!', 'Yousif', 'Khalid')[1]
    # create a channel
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    with pytest.raises(HTTPError):
        channel_messages(my_token, channel_id + 1, start=0)
    logout(my_token)


def test_channel_messages_invalid_token():
    '''
    Checking an invalid token raises an exception
    '''
    my_token = login('z5236259@unsw.edu.au', '1231FFF!')[1]
    # getting the available channel
    channel_id = channels_list(my_token)[0]['channel_id']
    # assertion
    with pytest.raises(HTTPError):
        channel_messages(my_token + 'a', channel_id, start=0)

# Testing channel_join


def test_channel_join_ok(reset):
    '''
    A valid request to join a channel
    '''
    owner_token = register('z5236259@unsw.edu.au',
                           '1231FFF!', 'Yousif', 'Khalid')[1]
    user_token = register('z123456@unsw.edu.au',
                          'bananaboy!', 'Jack', 'Robbers')[1]
    # create a channel
    channel_id = channels_create(
        owner_token, 'Yousifs Channel', is_public=True)
    channel_join(user_token, channel_id)
    message_send(user_token, channel_id, 'My first message!')


def test_channel_join_private(reset):
    '''
    An invalid request to join a private channel
    '''
    owner_token = register('z5236259@unsw.edu.au',
                           '1231FFF!', 'Yousif', 'Khalid')[1]
    user_token = register('z123456@unsw.edu.au',
                          'bananaboy!', 'Jack', 'Robbers')[1]
    # create a channel
    channel_id = channels_create(
        owner_token, 'Yousifs Channel', is_public=False)
    with pytest.raises(HTTPError):
        channel_join(user_token, channel_id)


def test_channel_join_invalid_token(reset):
    '''
    An invalid request with an invalid token
    '''
    owner_token = register('z5236259@unsw.edu.au',
                           '1231FFF!', 'Yousif', 'Khalid')[1]
    user_token = register('z123456@unsw.edu.au',
                          'bananaboy!', 'Jack', 'Robbers')[1]
    # create a channel
    channel_id = channels_create(
        owner_token, 'Yousifs Channel', is_public=False)
    with pytest.raises(HTTPError):
        channel_join(user_token + 'a', channel_id)


def test_channel_join_already_joined(reset):
    '''
    An invalid attempt to join an already joined channel
    '''
    owner_token = register('z5236259@unsw.edu.au',
                           '1231FFF!', 'Yousif', 'Khalid')[1]
    user_token = register('z123456@unsw.edu.au',
                          'bananaboy!', 'Jack', 'Robbers')[1]
    # create a channel
    channel_id = channels_create(
        owner_token, 'Yousifs Channel', is_public=True)
    channel_join(user_token, channel_id)
    with pytest.raises(HTTPError):
        channel_join(user_token, channel_id)
    # loggging out for next test
    logout(user_token)
    logout(owner_token)

# testing channel_leave


def test_channel_leave_ok():
    '''
    Testing leaving a channel
    '''
    user_token = login('z123456@unsw.edu.au', 'bananaboy!')[1]
    # getting the available channel
    channel_id = channels_list(user_token)[0]['channel_id']
    channel_leave(user_token, channel_id)
    # this means I can join once again without an issue
    channel_join(user_token, channel_id)


def test_channel_leave_not_a_member(reset):
    '''
    Invalid to leave a channel when not a member
    '''
    owner_token = register('z5236259@unsw.edu.au',
                           '1231FFF!', 'Yousif', 'Khalid')[1]
    user_token = register('z123456@unsw.edu.au',
                          'bananaboy!', 'Jack', 'Robbers')[1]
    # create a channel
    channel_id = channels_create(
        owner_token, 'Yousifs Channel', is_public=True)
    with pytest.raises(HTTPError):
        channel_leave(user_token, channel_id)

def test_channel_leave_invalid_token(reset):
    '''
    Invalid request with an invalid token
    '''
    owner_token = register('z5236259@unsw.edu.au',
                           '1231FFF!', 'Yousif', 'Khalid')[1]
    user_token = register('z123456@unsw.edu.au',
                          'bananaboy!', 'Jack', 'Robbers')[1]
    # create a channel
    channel_id = channels_create(
        owner_token, 'Yousifs Channel', is_public=True)
    channel_join(user_token, channel_id)
    with pytest.raises(HTTPError):
        channel_leave(user_token + 'a', channel_id)

# testing channel_addowner


def test_channel_addowner_ok(reset):
    '''
    A valid request to add a  user as an owner to a channel
    '''
    owner_token = register('z5236259@unsw.edu.au',
                           '1231FFF!', 'Yousif', 'Khalid')[1]
    user_id, user_token = register(
        'z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')
    # create a channel
    channel_id = channels_create(
        owner_token, 'Yousifs Channel', is_public=True)
    # make user owner
    channel_addowner(owner_token, channel_id, user_id)
    # send a generic message as an owner
    msg_id = message_send(owner_token, channel_id, 'owners message')
    # try to delete message
    message_remove(user_token, msg_id)


def test_channel_addowner_as_reg_member(reset):
    '''
    An Invalid request to add a user to a
    '''
    owner_token = register('z5236259@unsw.edu.au',
                           '1231FFF!', 'Yousif', 'Khalid')[1]
    user_id = register('z123456@unsw.edu.au',
                       'bananaboy!', 'Jack', 'Robbers')[0]
    imposer_token = register('z232332@unsw.edu.au',
                             '1234151', 'Koko', 'Lime')[1]
    # create a channel
    channel_id = channels_create(
        owner_token, 'Yousifs Channel', is_public=True)
    channel_join(imposer_token, channel_id)
    # assertion
    with pytest.raises(HTTPError):
        channel_addowner(imposer_token, channel_id, user_id)


def test_channel_addowner_already_owner(reset):
    '''
    Invalid request to add an owner as an owner
    '''
    owner_token = register('z5236259@unsw.edu.au',
                           '1231FFF!', 'Yousif', 'Khalid')[1]
    user_id = register('z123456@unsw.edu.au',
                       'bananaboy!', 'Jack', 'Robbers')[0]
    # create a channel
    channel_id = channels_create(
        owner_token, 'Yousifs Channel', is_public=True)
    # add owner
    channel_addowner(owner_token, channel_id, user_id)
    # add again..
    with pytest.raises(HTTPError):
        channel_addowner(owner_token, channel_id, user_id)


def test_channel_addowner_non_member(reset):
    '''
    An Invalid request to add a user to a
    '''
    owner_token = register('z5236259@unsw.edu.au',
                           '1231FFF!', 'Yousif', 'Khalid')[1]
    user_id = register('z123456@unsw.edu.au',
                       'bananaboy!', 'Jack', 'Robbers')[0]
    imposer_token = register('z232332@unsw.edu.au',
                             '1234151', 'Koko', 'Lime')[1]
    # create a channel
    channel_id = channels_create(
        owner_token, 'Yousifs Channel', is_public=True)
    # assertion
    with pytest.raises(HTTPError):
        channel_addowner(imposer_token, channel_id, user_id)


def test_channel_addowner_invalid_token(reset):
    '''
    Invalid request <=> invalid token
    '''
    owner_token = register('z5236259@unsw.edu.au',
                           '1231FFF!', 'Yousif', 'Khalid')[1]
    user_id = register('z123456@unsw.edu.au',
                       'bananaboy!', 'Jack', 'Robbers')[0]
    # create a channel
    channel_id = channels_create(
        owner_token, 'Yousifs Channel', is_public=True)
    # assertion
    with pytest.raises(HTTPError):
        channel_addowner(owner_token + 'a', channel_id, user_id)

# testing channel_removeowner


def test_channel_removeowner_ok(reset):
    '''
    Valid request to remove an owner
    '''
    owner_token = register('z5236259@unsw.edu.au',
                           '1231FFF!', 'Yousif', 'Khalid')[1]
    user_id, user_token = register(
        'z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')
    # create a channel
    channel_id = channels_create(
        owner_token, 'Yousifs Channel', is_public=True)
    # sending a message as owner
    msg_id = message_send(owner_token, channel_id, 'blabla')
    # adding then removing
    channel_addowner(owner_token, channel_id, user_id)
    channel_removeowner(owner_token, channel_id, user_id)
    try:
        message_remove(user_token, msg_id)
    except HTTPError:
        pass


def test_channel_removeowner_invalid_token(reset):
    '''
    Valid request to remove an owner
    '''
    owner_token = register('z5236259@unsw.edu.au',
                           '1231FFF!', 'Yousif', 'Khalid')[1]
    user_id = register('z123456@unsw.edu.au',
                       'bananaboy!', 'Jack', 'Robbers')[0]
    # create a channel
    channel_id = channels_create(
        owner_token, 'Yousifs Channel', is_public=True)
    # adding then removing
    channel_addowner(owner_token, channel_id, user_id)
    with pytest.raises(HTTPError):
        channel_removeowner(owner_token + 'a', channel_id, user_id)


def test_channel_removeowner_reg_member(reset):
    '''
    Invalid request to remove owner as non owner
    '''
    owner_id, owner_token = register(
        'z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')
    user_token = register('z123456@unsw.edu.au',
                          'bananaboy!', 'Jack', 'Robbers')[1]
    # create a channel
    channel_id = channels_create(
        owner_token, 'Yousifs Channel', is_public=True)
    # join channel
    channel_join(user_token, channel_id)
    with pytest.raises(HTTPError):
        channel_removeowner(user_token, channel_id, owner_id)


def test_channel_removeowner_already_not(reset):
    '''
    Invalid request to remove ownership from a non-owner
    '''
    owner_token = register('z5236259@unsw.edu.au',
                           '1231FFF!', 'Yousif', 'Khalid')[1]
    user_id, user_token = register(
        'z123456@unsw.edu.au', 'bananaboy!', 'Jack', 'Robbers')
    # create a channel
    channel_id = channels_create(
        owner_token, 'Yousifs Channel', is_public=True)
    # join channel
    channel_join(user_token, channel_id)
    with pytest.raises(HTTPError):
        channel_removeowner(owner_token, channel_id, user_id)


def test_channel_removeowner_not_a_member(reset):
    '''
    Invalid request to remove ownership being a non-member
    '''
    owner_id, owner_token = register(
        'z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')
    user_token = register('z123456@unsw.edu.au',
                          'bananaboy!', 'Jack', 'Robbers')[1]
    # create a channel
    channel_id = channels_create(
        owner_token, 'Yousifs Channel', is_public=True)
    with pytest.raises(HTTPError):
        channel_removeowner(user_token, channel_id, owner_id)
