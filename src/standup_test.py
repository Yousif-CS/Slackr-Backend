'''
This file contains tests for standup functions
'''
import time
from time import sleep
import pytest
import standup
from auth import auth_register, auth_logout
from channels import channels_create
from error import InputError, AccessError
from other import workspace_reset
from channel import channel_join, channel_messages

'''Fixtures to be used in testing'''


@pytest.fixture
def create_owner():
    '''
    Just a fixture to register an owner and return its details
    '''
    user_info = auth_register(
        "Yousif@gmail.com", "13131ABC", "Yousif", "Khalid")
    return user_info


@pytest.fixture
def create_user1():
    '''
    Create a general user and return its details
    '''
    user_info = auth_register("member@gmail.com", "12321AB", "John", "Wick")
    return user_info


@pytest.fixture
def create_user2():
    '''
    Create a general user and return its details
    '''
    user_info = auth_register("holaAmigos@gmail.com",
                              "123A456!", "Banana", "Guy")
    return user_info


@pytest.fixture
def create_public_channel():
    '''
    Create a public channel using the owner fixture and return their details
    '''
    workspace_reset()
    owner_info = auth_register(
        "Yousif@gmail.com", "13131ABC", "Yousif", "Khalid")
    channel_id = channels_create(owner_info['token'], 'test_channel', True)
    return (channel_id, owner_info)


@pytest.fixture
def create_private_channel():
    '''
    Create a private channel using the owner fixture and return their details
    '''
    owner_info = auth_register(
        "Yousif@gmail.com", "13131ABC", "Yousif", "Khalid")
    channel_id = channels_create(owner_info['token'], 'test_channel', False)
    return (channel_id, owner_info)


'''Testing standup_start'''


def test_standup_send_invalid_length(create_public_channel):
    '''
    Tests an invalid input
    '''
    new_ch, owner = create_public_channel
    with pytest.raises(InputError):
        standup.standup_start(owner['token'], new_ch['channel_id'], length='a')

# AccessError: invalid token


def test_standup_start_invalid_token(create_public_channel):
    '''
    Invalid token check
    '''
    new_ch, owner = create_public_channel
    with pytest.raises(AccessError):
        standup.standup_start(
            owner["token"] + "invalid", new_ch["channel_id"], 2)

# InputError: channel ID not a valid channel


def test_standup_start_invalid_channel(create_public_channel):
    '''
    Invalid channel check
    '''
    new_ch, owner = create_public_channel
    with pytest.raises(InputError):
        standup.standup_start(owner["token"], new_ch["channel_id"] + 1, 2)

# InputError: active standup is currently running in this channel


def test_standup_start_overlap(create_public_channel):
    '''
    Double standup start in the same channel
    '''
    new_ch, owner = create_public_channel
    standup.standup_start(owner["token"], new_ch["channel_id"], 2)
    with pytest.raises(InputError):
        standup.standup_start(owner["token"], new_ch["channel_id"], 2)
    sleep(2.1)
    standup.standup_start(owner["token"], new_ch["channel_id"], 2)

# Starts the standup period whereby for the next "length" seconds if someone calls "standup_send" with a message,
# #it is buffered during the X second window then at the end of the X second window a message will be added to
# the message queue in the channel from the user who started the standup.


def test_standup_in_action(create_public_channel):
    '''
    Test the ability to send messages in the standup
    '''
    new_ch, owner = create_public_channel

    user1 = auth_register("joshwang@gmail.com",
                          "asdfjkasdfjlaskdf", "Josh", "Wang")
    user2 = auth_register("kenli@hotmail.com", "kajfsd;jkas;31", "Ken", "Li")
    user3 = auth_register("maximation@yahoo.com.au",
                          "3456789osd", "Max", "Smith")

    channel_join(user1["token"], new_ch["channel_id"])
    channel_join(user2["token"], new_ch["channel_id"])
    channel_join(user3["token"], new_ch["channel_id"])

    standup.standup_start(owner["token"], new_ch["channel_id"], 2)
    assert standup.standup_active(owner["token"], new_ch["channel_id"])[
        "is_active"] is True

    standup.standup_send(
        owner["token"], new_ch["channel_id"], "On sundae I ate a Sunday")
    standup.standup_send(
        user1["token"], new_ch["channel_id"], "Is this the real life?")
    standup.standup_send(
        user2["token"], new_ch["channel_id"], "Or is this just fantasy?")
    standup.standup_send(
        user3["token"], new_ch["channel_id"], "Caught in a landslide,")
    standup.standup_send(
        owner["token"], new_ch["channel_id"], "No escape from reality.")

    sleep(2.1)
    # getting the messages
    messages = channel_messages(
        owner['token'], new_ch['channel_id'], start=0)['messages']
    # prepping the sent message for assert
    sent_msgs = ["On sundae I ate a Sunday", "Is this the real life?",
                 "Or is this just fantasy?", "Caught in a landslide,",
                 "No escape from reality."]
    buffered_msg = '\n'.join(sent_msgs)

    assert messages[0]['message'] == buffered_msg


def test_standup_start_by_normal_member(create_public_channel):
    '''
    Testing starting a standup by a normal member
    '''
    new_ch, owner = create_public_channel

    user1 = auth_register("joshwang@gmail.com",
                          "asdfjkasdfjlaskdf", "Josh", "Wang")
    channel_join(user1["token"], new_ch["channel_id"])

    standup.standup_start(user1["token"], new_ch["channel_id"], 3)
    assert standup.standup_active(owner["token"], new_ch["channel_id"])[
        "is_active"] is True


'''Testing standup_active'''


def test_standup_active_invalid_channel(create_public_channel):
    '''
    Testing whether the function throws an exception given an invalid channel_id
    '''
    # creating a public channel
    channel_id, owner_info = create_public_channel
    # testing an invalid channel id produces an exception
    with pytest.raises(InputError):
        standup.standup_active(
            owner_info['token'], channel_id['channel_id'] + 1)


def test_standup_active_inactive(create_public_channel):
    '''
    Testing calling the function with no active standup
    '''
    # creating a public channel
    channel_id, owner_info = create_public_channel
    # getting the details
    standup_details = standup.standup_active(
        owner_info['token'], channel_id['channel_id'])
    assert standup_details['is_active'] is False
    assert standup_details['time_finish'] is None


def test_standup_active_active(create_public_channel):
    '''
    Testing calling the function with an active standup
    '''
    # creating a public channel
    channel_id, owner_info = create_public_channel
    # starting a standup
    time_finish = standup.standup_start(
        owner_info['token'], channel_id['channel_id'], 2)["time_finish"]
    # getting the standup active status
    standup_details = standup.standup_active(
        owner_info['token'], channel_id['channel_id'])
    # asserting
    assert standup_details['is_active'] is True
    assert standup_details['time_finish'] == time_finish


def test_standup_active_finished(create_public_channel):
    '''
    Testing calling the function after a standup has ended
    '''
    # creating a public channel
    channel_id, owner_info = create_public_channel
    # starting a standup
    time_finish = standup.standup_start(
        owner_info['token'], channel_id['channel_id'], 2)
    time.sleep(2.1)  # sleep for 4 seconds
    # getting the standup active status
    standup_details = standup.standup_active(
        owner_info['token'], channel_id['channel_id'])
    # asserting
    assert standup_details['is_active'] is False
    assert standup_details['time_finish'] is None


def test_standup_active_invalid_token(create_public_channel):
    '''
    Testing using an invalid token while calling the function -> accessError
    '''
    # creating a public channel
    channel_id, owner_info = create_public_channel
    # starting a standup
    with pytest.raises(AccessError):
        standup_details = standup.standup_active(
            owner_info['token'] + str(1), channel_id['channel_id'])


'''Testing standup_send'''


def test_standup_send_invalid_channel(create_public_channel):
    '''
    Testing calling the function with an invalid channel_id
    '''
    # creating a public channel
    channel_id, owner_info = create_public_channel
    # starting a standup
    time_finish = standup.standup_start(
        owner_info['token'], channel_id['channel_id'], 3)
    # sending a message to a standup
    with pytest.raises(InputError):
        standup.standup_send(
            owner_info['token'], channel_id['channel_id'] + 1, "My standup!")


def test_standup_send_no_active_standup(create_public_channel):
    '''
    Testing sending a message to a non-existent standup
    '''
    # creating a public channel
    channel_id, owner_info = create_public_channel
    with pytest.raises(InputError):
        standup.standup_send(
            owner_info['token'], channel_id['channel_id'], "My first standup!")


def test_standup_send_finished_standup(create_public_channel):
    '''
    Testing sending a message to an already finished standup
    '''
    # creating a public channel
    channel_id, owner_info = create_public_channel
    # start a standup
    time_finish = standup.standup_start(
        owner_info['token'], channel_id['channel_id'], 3)
    # sleep for a bit
    time.sleep(5)
    with pytest.raises(InputError):
        standup.standup_send(
            owner_info['token'], channel_id['channel_id'], "My first standup!")


def test_standup_send_long_message(create_public_channel):
    '''
    Testing sending a very long message ( > 1000) results in an exception
    '''
    # creating a public channel
    channel_id, owner_info = create_public_channel
    # start a standup
    time_finish = standup.standup_start(
        owner_info['token'], channel_id['channel_id'], 3)
    # sending
    with pytest.raises(InputError):
        standup.standup_send(
            owner_info['token'], channel_id['channel_id'], "a" * 1001)


def test_standup_send_non_member(create_public_channel, create_user1):
    '''
    Testing trying to send to a channel's standup that we do not belong to
    '''
    # creating a public channel
    channel_id, owner_info = create_public_channel
    # creating a general user
    user_info = create_user1
    # creating a standup
    time_finish = standup.standup_start(
        owner_info['token'], channel_id['channel_id'], 3)
    # sending
    with pytest.raises(AccessError):
        standup.standup_send(user_info['token'],
                             channel_id['channel_id'], "Intruder!")


def test_standup_send_empty_message(create_public_channel):
    '''
    Testing trying to send an empty message to a standup ignores the message
    '''
    # creating a public channel
    channel_id, owner_info = create_public_channel
    # creating a standup
    time_finish = standup.standup_start(
        owner_info['token'], channel_id['channel_id'], 3)
    # sending
    with pytest.raises(InputError):
        standup.standup_send(owner_info['token'], channel_id['channel_id'], "")


def test_standup_send_invalid_token(create_public_channel):
    '''
    Testing using an invalid token while calling the function -> accessError
    '''
    # creating a public channel
    channel_id, owner_info = create_public_channel
    # starting a standup
    with pytest.raises(AccessError):
        standup.standup_send(
            owner_info['token'] + str(1), channel_id['channel_id'], "Aaaahhh!")


def test_standup_send_starter_is_logged_out(create_public_channel, create_user1):
    '''
    Testing to see if a standup is resolved even if the invoker is logged out
    '''
    # creating a public channel
    channel_id, owner_info = create_public_channel
    user_info = create_user1
    # user joins channel
    channel_join(user_info['token'], channel_id['channel_id'])
    # owner starts standup
    standup.standup_start(owner_info['token'],
                          channel_id['channel_id'], length=2)
    # owner logs out
    auth_logout(owner_info['token'])
    # user sends message
    standup.standup_send(user_info['token'], channel_id['channel_id'], 'hola!')
    sleep(2.5)
    messages = channel_messages(
        user_info['token'], channel_id['channel_id'], start=0)['messages']
    assert messages[0]['message'] == 'hola!'
    assert messages[0]['u_id'] == owner_info['u_id']
