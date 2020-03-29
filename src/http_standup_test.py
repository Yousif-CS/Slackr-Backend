'''
HTTP tests for standups
'''

import time
from urllib.error import HTTPError
import pytest

from http_helpers import (reset, register,
                          message_send, channels_create,
                          channel_messages, channel_join,
                          standup_start, standup_active,
                          standup_send)

#testing standup start

def test_standup_start_invalid_token(reset):
    '''
    Invalid request with an invalid token
    '''
    my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    with pytest.raises(HTTPError):
        standup_start(my_token + 'a', channel_id, length=2)

def test_standup_start_invalid_channel_id(reset):
    '''
    Invalid request by using an invalid channel_id
    '''
    my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    with pytest.raises(HTTPError):
        standup_start(my_token, channel_id + 1, length=2)

def test_standup_start_more_than_one(reset):
    '''
    Invalid request starting more than one standup in the channel
    '''
    my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    standup_start(my_token, channel_id, length=3)
    with pytest.raises(HTTPError):
        standup_start(my_token, channel_id, length=2)

def test_standup_start_after_last_finished(reset):
    '''
    A valid request to start a standup after the previous one has finished
    '''
    my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)

    standup_start(my_token, channel_id, length=2)
    time.sleep(2.1)
    standup_start(my_token, channel_id, length=2)

#testing standup_active
def test_standup_active_ok(reset):
    '''
    Checking if a standup is active inside a channel
    '''
    my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    finish_time = time.time() + 3
    #creating a standup
    standup_start(my_token, channel_id, length=3)
    is_active, standup_finish = standup_active(my_token, channel_id)
    time.sleep(1)
    #should be active
    assert is_active
    assert standup_finish - finish_time < 1 #have to account for delay
    time.sleep(2)
    #checking once again => shouldn't be active
    is_active, standup_finish = standup_active(my_token, channel_id)
    assert not is_active
    assert standup_finish is None

def test_standup_active_no_active_standups(reset):
    '''
    A valid request where no standups should be active
    '''
    my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    is_active, finish_time = standup_active(my_token, channel_id)
    assert not is_active
    assert finish_time is None

def test_standup_active_invalid_channel_id(reset):
    '''
    Invalid request with an invalid channel id
    '''
    my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    with pytest.raises(HTTPError):
        standup_active(my_token, channel_id + 1)

def test_standup_active_invalid_token(reset):
    '''
    Invalid request with invalid token
    '''
    my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    with pytest.raises(HTTPError):
        standup_active(my_token + 'a', channel_id)

#Testing standup_send
def test_standup_send_invalid_token(reset):
    '''
    Invalid request with invalid token
    '''
    my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    standup_start(my_token, channel_id, length=3)
    with pytest.raises(HTTPError):
        standup_send(my_token + 'a', channel_id, 'my first message!')

def test_standup_send_one_message(reset):
    '''
    A valid request to send a message to a standup
    '''
    my_id, my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    standup_start(my_token, channel_id, length=3)
    standup_send(my_token, channel_id, 'Actually my first message?')
    time.sleep(3.1)
    messages = channel_messages(my_token, channel_id, start=0)[0]
    assert messages[0]['message'] == 'Actually my first message?'
    assert messages[0]['u_id'] == my_id

def test_standup_send_two_messages(reset):
    '''
    A valid request to send two messages to a standup
    '''
    my_id, my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')
    user_token = register('z5222222@unsw.edu.au', '2222!!!!', 'Jack', 'Robbers')[1]
    #creating a channel
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    #other user joins
    channel_join(user_token, channel_id)
    #starting a standup by me
    standup_start(my_token, channel_id, length=3)
    #message sent by me
    standup_send(my_token, channel_id, 'Actually my first message?')
    #message sent by another guy
    standup_send(user_token, channel_id, 'Jacks message!')
    time.sleep(3.1)
    messages = channel_messages(my_token, channel_id, start=0)[0]
    assert messages[0]['message'] == 'Actually my first message?\nJacks message!'
    assert messages[0]['u_id'] == my_id

def test_standup_send_non_member(reset):
    '''
    Invalid request made by a non-member
    '''
    my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    user_token = register('z5222222@unsw.edu.au', '2222!!!!', 'Jack', 'Robbers')[1]
    #creating a channel
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)

    #starting a standup by me
    standup_start(my_token, channel_id, length=3)
    #message sent by me
    standup_send(my_token, channel_id, 'Actually my first message?')
    #message sent by another guy
    with pytest.raises(HTTPError):
        standup_send(user_token, channel_id, 'Jacks message!')

def test_standup_send_standup_finished(reset):
    '''
    Invalid request to send into an already finished standup
    '''
    my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    #creating a channel
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)

    #starting a standup by me
    standup_start(my_token, channel_id, length=2)
    #message sent by me
    time.sleep(2.1)
    with pytest.raises(HTTPError):
        standup_send(my_token, channel_id, 'Actually my first message?')

def test_standup_send_invalid_channel(reset):
    '''
    Testing a sending to an invalid channel id
    '''
    my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    #creating a channel
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)

    #starting a standup by me
    standup_start(my_token, channel_id, length=2)
    #message sent by me
    with pytest.raises(HTTPError):
        standup_send(my_token, channel_id + 2, 'Actually my first message?')

def test_standup_send_non_blocking(reset):
    '''
    Testing tinkering with standups does not block other things
    '''
    my_token = register('z5236259@unsw.edu.au', '1231FFF!', 'Yousif', 'Khalid')[1]
    #creating a channel
    channel_id = channels_create(my_token, 'Yousifs Channel', is_public=True)
    #starting a standup by me
    standup_start(my_token, channel_id, length=3)
    #message sent by me
    standup_send(my_token, channel_id, 'should be last message sent pt1')
    standup_send(my_token, channel_id, 'should be last message sent pt2')

    message_send(my_token, channel_id, 'should be first message sent')
    time.sleep(3.1)
    messages = channel_messages(my_token, channel_id, start=0)[0]
    assert len(messages) == 2
    assert messages[0]['message'] == \
        'should be last message sent pt1\nshould be last message sent pt2'
 