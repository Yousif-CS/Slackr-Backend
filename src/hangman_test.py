'''
Integration tests for hangman
'''

#pylint: disable=missing-function-docstring
#pylint: disable=redefined-outer-name
#pylint: disable=trailing-whitespace

import pytest #pylint: disable=import-error
from error import InputError, AccessError
from hangman import generate_word, start_game, guess
from message import message_send
from channels import channels_create
from channel import channel_messages
from auth import auth_register, auth_logout
from other import workspace_reset

@pytest.fixture
def reset():
    workspace_reset()

def test_generate_word(reset):
    assert len(generate_word()) <= 10
    assert len(generate_word()) <= 10
    assert len(generate_word()) <= 10
    assert len(generate_word()) <= 10
    assert len(generate_word()) <= 10
    assert len(generate_word()) <= 10
    assert len(generate_word()) <= 10
    assert len(generate_word()) <= 10
    assert len(generate_word()) <= 10
    assert len(generate_word()) <= 10
    assert len(generate_word()) <= 10

def test_start_game(reset):
    owner = auth_register("help@email.com", "quarantine driving me crazy", "bot", "aksd")
    new_ch = channels_create(owner['token'], 'Channel1', is_public=True)
    data = start_game(new_ch['channel_id'])
    assert data == ''
    message_send(owner['token'], new_ch['channel_id'], '/hangman') 
    message_send(owner['token'], new_ch['channel_id'], '/guess E') 
    assert channel_messages(owner['token'], new_ch['channel_id'], 0)== ''

def test_hangman(reset):
    owner = auth_register("help@email.com", "quarantine driving me crazy", "bot", "aksd")
    new_ch = channels_create(owner['token'], 'Channel1', is_public=True)
    msg1 = message_send(owner['token'], new_ch['channel_id'], "/hangman")

    msg_view = channel_messages(owner['token'], new_ch['channel_id'], 0)
    first_msg = msg_view['messages'][0]

    assert first_msg['message_id'] == msg1['message_id']
    assert first_msg['u_id'] == owner['u_id']
    assert first_msg['message'] == '/hangman'
