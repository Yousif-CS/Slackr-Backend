'''
Integration tests for functions in other.py
'''

#pylint: disable=redefined-outer-name
#pylint: disable=pointless-string-statement
#pylint: disable=missing-function-docstring
#pylint: disable=unused-argument

import pytest
from other import users_all, search, userpermission_change, user_remove, workspace_reset
from auth import auth_register, auth_logout
from channels import channels_create
from message import message_send
from error import InputError, AccessError
from channel import channel_invite, channel_join, channel_leave, channel_messages, channel_details


SLACKR_OWNER = 1
SLACKR_MEMBER = 2
INVALID_PERMISSION = 3


@pytest.fixture
def reset():
    workspace_reset()


@pytest.fixture
def make_user_ab():
    user_ab = auth_register(
        "alice@gmail.com", "stronkpassword123", "Alice", "Bee")
    return user_ab


@pytest.fixture
def make_user_cd():
    user_cd = auth_register("charlie@gmail.com",
                            "comp1531pass", "Charlie", "Dee")
    return user_cd


# These users are designed for the users_all function for Josh
@pytest.fixture
def make_user_ef():
    user_ef = auth_register(
        "edward@gmail.com", "12345687", "Edward", "Frankenstein")
    return (user_ef["token"], user_ef["u_id"])


@pytest.fixture
def make_user_gh():
    user_gh = auth_register("gregory@gmail.com",
                            "ihaveadream", "Gregory", "Heidelberg")
    return (user_gh["token"], user_gh["u_id"])


@pytest.fixture
def make_user_ij():
    user_ij = auth_register(
        "ian@hotmail.com", "stretchy0urh4mstrinG5thr1c3", "Ian", "Jacobs")
    return (user_ij["token"], user_ij["u_id"])
###


@pytest.fixture
def create_public_channel(make_user_ab):
    user_ab = make_user_ab
    channel_id = channels_create(user_ab['token'], 'test_channel_public', True)
    return (channel_id, user_ab)


@pytest.fixture
def create_private_channel(make_user_ab):
    user_ab = make_user_ab
    channel_id = channels_create(
        user_ab['token'], 'test_channel_private', False)
    return (channel_id, user_ab)


'''------------------testing users_all--------------------'''
# returns a dictionary of a list containing all the users

# start with only one user accessing all users


def test_users_all_one_user():
    workspace_reset()
    user_ef = auth_register(
        "edward@gmail.com", "12345687", "Edward", "Frankenstein")

    assert users_all(user_ef["token"])["users"] == [
        {
            'u_id': user_ef["u_id"],
            'email': 'edward@gmail.com',
            'name_first': 'Edward',
            'name_last': 'Frankenstein',
            'handle_str': 'edwardfrankenstein'
        }
    ]


def test_users_all_access_three_users_at_once_in_order():
    workspace_reset()
    user_gh = auth_register("gregory@gmail.com",
                            "ihaveadream", "Gregory", "Heidelberg")
    user_ef = auth_register(
        "edward@gmail.com", "12345687", "Edward", "Frankenstein")
    user_ij = auth_register(
        "ian@hotmail.com", "stretchy0urh4mstrinG5thr1c3", "Ian", "Jacobs")

    assert users_all(user_ij["token"])["users"] == [
        {
            'u_id': user_gh["u_id"],
            'email': 'gregory@gmail.com',
            'name_first': 'Gregory',
            'name_last': 'Heidelberg',
            'handle_str': 'gregoryheidelberg'
        },
        {
            'u_id': user_ef["u_id"],
            'email': 'edward@gmail.com',
            'name_first': 'Edward',
            'name_last': 'Frankenstein',
            'handle_str': 'edwardfrankenstein'
        },
        {
            'u_id': user_ij["u_id"],
            'email': 'ian@hotmail.com',
            'name_first': 'Ian',
            'name_last': 'Jacobs',
            'handle_str': 'ianjacobs'
        }
    ]

# register the users one at a time and access all the users


def test_users_all_register_and_call_function_one_at_a_time():
    workspace_reset()
    user_gh = auth_register("gregory@gmail.com",
                            "ihaveadream", "Gregory", "Heidelberg")
    user_ef = auth_register(
        "edward@gmail.com", "12345687", "Edward", "Frankenstein")

    assert users_all(user_ef["token"])["users"] == [
        {
            'u_id': user_gh["u_id"],
            'email': 'gregory@gmail.com',
            'name_first': 'Gregory',
            'name_last': 'Heidelberg',
            'handle_str': 'gregoryheidelberg'
        },
        {
            'u_id': user_ef["u_id"],
            'email': 'edward@gmail.com',
            'name_first': 'Edward',
            'name_last': 'Frankenstein',
            'handle_str': 'edwardfrankenstein'
        }
    ]

    user_ij = auth_register(
        "ian@hotmail.com", "stretchy0urh4mstrinG5thr1c3", "Ian", "Jacobs")
    assert users_all(user_ij["token"])["users"] == [
        {
            'u_id': user_gh["u_id"],
            'email': 'gregory@gmail.com',
            'name_first': 'Gregory',
            'name_last': 'Heidelberg',
            'handle_str': 'gregoryheidelberg'
        },
        {
            'u_id': user_ef["u_id"],
            'email': 'edward@gmail.com',
            'name_first': 'Edward',
            'name_last': 'Frankenstein',
            'handle_str': 'edwardfrankenstein'
        },
        {
            'u_id': user_ij["u_id"],
            'email': 'ian@hotmail.com',
            'name_first': 'Ian',
            'name_last': 'Jacobs',
            'handle_str': 'ianjacobs'
        }
    ]


def test_users_all_users_remain_when_logout():
    workspace_reset()
    user_gh = auth_register("gregory@gmail.com",
                            "ihaveadream", "Gregory", "Heidelberg")
    user_ef = auth_register(
        "edward@gmail.com", "12345687", "Edward", "Frankenstein")
    user_ij = auth_register(
        "ian@hotmail.com", "stretchy0urh4mstrinG5thr1c3", "Ian", "Jacobs")
    auth_logout(user_ef["token"])

    assert users_all(user_ij["token"])["users"] == [
        {
            'u_id': user_gh["u_id"],
            'email': 'gregory@gmail.com',
            'name_first': 'Gregory',
            'name_last': 'Heidelberg',
            'handle_str': 'gregoryheidelberg'
        },
        {
            'u_id': user_ef["u_id"],
            'email': 'edward@gmail.com',
            'name_first': 'Edward',
            'name_last': 'Frankenstein',
            'handle_str': 'edwardfrankenstein'
        },
        {
            'u_id': user_ij["u_id"],
            'email': 'ian@hotmail.com',
            'name_first': 'Ian',
            'name_last': 'Jacobs',
            'handle_str': 'ianjacobs'
        }
    ]


def test_users_all_invalid_token_error():
    workspace_reset()
    user_ef = auth_register(
        "edward@gmail.com", "12345687", "Edward", "Frankenstein")

    with pytest.raises(AccessError):
        users_all(user_ef["token"] + "invalid")


'''------------------testing search--------------------'''
# reminder
# input: (token, query_str); output: {messages}
# returns messages in ALL channels that user is in

# Search string tests:
# testing that empty search string should return empty dictionary


def test_search_empty_string(reset, create_public_channel):
    new_public_channel, user_ab = create_public_channel
    message_send(user_ab['token'], new_public_channel['channel_id'], "Hello world!")

    assert search(user_ab['token'], "")['messages'] == []


# spaces in search string
def test_search_space_string(reset, create_public_channel):
    new_public_channel, user_ab = create_public_channel
    msg1 = message_send(
        user_ab['token'], new_public_channel['channel_id'], "A message with spaces!")
    # result_list is of type list (list of dictionaries)
    result_list = search(user_ab['token'], " ")['messages']

    # getting the message string
    messages = [message['message'] for message in result_list]
    # getting the message id and user ids that sent them
    messages_ids = [message['message_id'] for message in result_list]
    # getting the user ids of the senders
    u_ids = [message['u_id'] for message in result_list]

    assert msg1['message_id'] in messages_ids
    assert user_ab['u_id'] in u_ids
    assert "A message with spaces!" in messages


# letters and symbols in search string (combination of above)
def test_search_normal_string(reset, create_public_channel):

    new_public_channel, user_ab = create_public_channel
    msg1 = message_send(
        user_ab['token'], new_public_channel['channel_id'], "Symbols & words")
    msg2 = message_send(
        user_ab['token'], new_public_channel['channel_id'], "& with more stuff")
    message_send(
        user_ab['token'], new_public_channel['channel_id'], "hola amigos!")

    # result_list is of type list (list of dictionaries)
    result_list = search(user_ab['token'], "& w")['messages']

    # getting the message id and user ids that sent them
    messages_ids = [message['message_id'] for message in result_list]
    # getting the message string
    messages = [message['message'] for message in result_list]

    # asserting we found the messages
    assert msg1['message_id'] in messages_ids
    assert msg2['message_id'] in messages_ids

    # asserting the messages haven't been truncated or tampered with
    assert 'Symbols & words' in messages
    assert '& with more stuff' in messages


# search string is exactly message
def test_search_exact_string(reset, create_public_channel):
    new_public_channel, user_ab = create_public_channel
    message_send(user_ab['token'], new_public_channel['channel_id'],
                 "This is a very generic message")
    message_send(user_ab['token'], new_public_channel['channel_id'], "generic message")
    # search string matches a message exactly
    result_list = search(user_ab['token'], "This is a very generic message")[
        'messages']

    # getting the message string and user ids that sent them
    messages = [message['message'] for message in result_list]

    assert len(result_list) == 1
    assert "This is a very generic message" in messages


# search string longer than message (should be no match)
def test_search_string_too_long(reset, create_public_channel):
    new_public_channel, user_ab = create_public_channel
    message_send(
        user_ab['token'], new_public_channel['channel_id'], "Short string")
    # search string contains string but is longer than string
    result_list = search(user_ab['token'], "& w")['messages']

    # checking that the search returns nothing
    assert result_list == []


# Cross-channel tests
# multiple matching messages in different channels a user is in
def test_search_string_in_multiple_channels(reset, create_public_channel, make_user_cd):
    # user_ab creates public channel and sends a message to it
    new_public_channel, user_ab = create_public_channel
    message_send(
        user_ab['token'], new_public_channel['channel_id'], "ab's public channel message")
    # user_cd creates private channel and sends a message to it
    user_cd = make_user_cd
    new_private_channel = channels_create(
        user_cd['token'], "cd_private", False)
    message_send(
        user_cd['token'], new_private_channel['channel_id'], "cd's private channel message")
    # user_cd invites user_ab to private channel
    channel_invite(user_cd['token'],
                   new_private_channel['channel_id'], user_ab['u_id'])
    result_list = search(user_ab['token'], "channel message")['messages']

    # getting the message string and user ids that sent them
    messages = [message['message'] for message in result_list]
    u_ids = [message['u_id'] for message in result_list]

    # asserting the u_ids relate to the messages
    assert user_cd['u_id'] in u_ids
    assert user_ab['u_id'] in u_ids

    # asserting the messages are in the results
    assert "ab's public channel message" in messages
    assert "cd's private channel message" in messages


# matching messages in unjoined channel shold not show up
def test_search_string_in_unjoined_channel(reset, create_public_channel, make_user_cd):
    new_public_channel, user_ab = create_public_channel
    user_cd = make_user_cd
    message_send(
        user_ab['token'], new_public_channel['channel_id'], "ab's new public channel")
    # user_cd searches without joining the channel
    result_list = search(user_cd['token'], "public channel")['messages']

    assert result_list == []


# Exceptions
# 1000 + long search string gives error
def test_search_invalid_search_string(reset, create_public_channel):
    new_public_channel, user_ab = create_public_channel
    message_send(
        user_ab['token'], new_public_channel['channel_id'], "My first message")

    with pytest.raises(InputError):
        search(user_ab['token'], "My first message" + "a" * 999)

# invalid token
# assuming the token with string "invalid" is an invalid token


def test_search_invalid_token(reset, create_public_channel):
    user_ab = create_public_channel[1]

    with pytest.raises(AccessError):
        search(user_ab['token'] + 'a', "Search string")


'''Testing userpermission_change'''


def test_userpermission_change_invalid_token(reset, create_public_channel, make_user_ab):
    '''
    Testing using an invalid token
    '''

    # creating a public channel
    owner_info = create_public_channel[1]
    user1 = make_user_ab
    with pytest.raises(AccessError):
        userpermission_change(
            owner_info['token'] + 'a', user1['u_id'], SLACKR_OWNER)


def test_userpermission_change_invalid_u_id(reset, create_public_channel, make_user_ab):
    '''
    Changing permissions of a non-existent user
    '''

    # creating a public channel
    owner_info = create_public_channel[1]
    # since owner is the first user who signs up in this
    # test, he should be a slackr owner

    # giving admin permissions to a non-existent user
    with pytest.raises(InputError):
        userpermission_change(
            owner_info['token'], owner_info['u_id'] + 1, SLACKR_OWNER)

def test_userpermission_change_permission_denied(reset, create_public_channel,
                                                 make_user_ab, make_user_cd):
    '''
    Trying to change another user's permissions as a non-slackr-owner
    '''
    # creating a public channel
    create_public_channel #pylint: disable=pointless-statement
    # since owner is the first user who signs up in this
    # test, he should be a slackr owner

    # create 2 general users
    user_ab_info = make_user_ab
    user_cd_info = make_user_cd
    # changing permissions
    with pytest.raises(AccessError):
        userpermission_change(
            user_cd_info['token'], user_ab_info['u_id'], SLACKR_OWNER)


def test_userpermission_change_invalid_permission(reset, create_public_channel, make_user_ab):
    '''
    Testing changing a user's permissions to an invalid one
    '''
    # creating a public channel
    owner_info = create_public_channel[1]
    # since owner is the first user who signs up in this
    # test, he should be a slackr owner

    # create a general user
    user_info = make_user_ab

    with pytest.raises(InputError):
        userpermission_change(
            owner_info['token'], user_info['u_id'], INVALID_PERMISSION)


def test_userpermission_change_invalid_permission_type(reset, create_public_channel, make_user_ab):
    '''
    Testing changing a user's permissions to an invalid one
    '''
    # creating a public channel
    owner_info = create_public_channel[1]
    # since owner is the first user who signs up in this
    # test, he should be a slackr owner

    # create a general user
    user_info = make_user_ab

    with pytest.raises(InputError):
        userpermission_change(
            owner_info['token'], user_info['u_id'], "You should complain")


def test_userpermission_change_promote(reset, create_private_channel, make_user_ab, make_user_cd):
    '''
    Testing promoting a user allows him to join private channels
    '''
    # creating a public channel
    channel_id, owner_info = create_private_channel
    # since owner is the first user who signs up in this
    # test, he should be a slackr owner

    # create a general user
    make_user_ab #pylint: disable=pointless-statement
    general_user = make_user_cd

    # testing joining a private channel
    try:
        channel_join(general_user['token'], channel_id['channel_id'])
        assert False
    except AccessError:
        userpermission_change(
            owner_info['token'], general_user['u_id'], SLACKR_OWNER)
        try:
            channel_join(general_user['token'], channel_id['channel_id'])
        except AccessError:
            assert False


def test_userpermission_change_demote(reset, create_private_channel, make_user_ab, make_user_cd):
    '''
    Testing demoting a user restricts him to join private channels
    '''
    # creating a private channel
    channel_id, owner_info = create_private_channel
    # since owner is the first user who signs up in this
    # test, he should be a slackr owner

    # create two users
    user_info = make_user_ab
    general_user = make_user_cd

    # promoting user
    userpermission_change(owner_info['token'], user_info['u_id'], SLACKR_OWNER)

    # Inviting a new user
    channel_invite(owner_info['token'],
                   channel_id['channel_id'], general_user['u_id'])

    # demoting user
    userpermission_change(owner_info['token'],
                          user_info['u_id'], SLACKR_MEMBER)

    # User leaves the channel
    channel_leave(user_info['token'], user_info['u_id'])

    # testing joining a private channel
    with pytest.raises(AccessError):
        channel_join(user_info['token'], channel_id['channel_id'])


def test_user_remove_no_user(reset, create_public_channel, make_user_ab):
    '''
    Testing removing a non-existent user
    '''
    # creating a public channel
    _, owner_info = create_public_channel
    with pytest.raises(InputError):
        user_remove(owner_info['token'], owner_info['u_id'] + 1)

def test_user_remove_invalid_token(reset, create_public_channel, make_user_ab):
    '''
    Invalid token raises AccessError
    '''
    # creating a public channel
    _, owner_info = create_public_channel
    # create user
    user_info = make_user_ab

    with pytest.raises(InputError):
        user_remove(owner_info['token'] + 1, user_info['u_id'])

def test_user_remove_not_admin(reset, make_user_ab, make_user_cd, make_user_ef):
    '''
    A reguler member tries to remove user
    '''
    # creating a public channel
    admin_info = make_user_ab
    # create users
    user1_info = make_user_cd
    user2_info = make_user_ef

    with pytest.raises(AccessError):
        user_remove(user1_info['token'], user2_info['u_id'])

def test_user_remove_messages_removed(reset, create_public_channel, make_user_ab):
    '''
    Testing if the users messages are removed
    '''
    # creating a public channel
    channel_id, owner_info = create_public_channel

    # creating user
    user_info = make_user_ab
    #joining and sending a message
    channel_join(user_info['token'], channel_id['channel_id'])
    message_send(user_info['token'], channel_id['channel_id'], 'HelloWorld')
    #removing user
    user_remove(owner_info['token'], user_info['u_id'])
    #should be empty
    messages = channel_messages(owner_info['token'], channel_id['channel_id'], start=0)
    assert len(messages['messages']) == 0

def test_user_remove_removed_from_channel(reset, create_public_channel, make_user_ab):
    # creating a public channel
    channel_id, owner_info = create_public_channel

    # creating user
    user_info = make_user_ab
    #joining
    channel_join(user_info['token'], channel_id['channel_id'])
    #removing user
    user_remove(owner_info['token'], user_info['u_id'])
    #getting the details of the channel
    ch_details = channel_details(owner_info['token'], channel_id['channel_id'])
    assert len(ch_details['all_members'] == 1)
