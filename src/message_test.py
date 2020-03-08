# TODO: import more modules / functions as needed 

from message import message_send, message_remove, message_edit
from error import AccessError, InputError
from auth import auth_login, auth_register
from channel import channel_invite, channel_details, channel_messages, channel_leave, \
     channel_join, channel_addowner, channel_removeowner
from channels import channels_create
from other import search
import pytest

# reminders: white space / empty messages? 
# invalid user token? throws Exception?

@pytest.fixture
def make_user_ab():
    user_ab = auth_register("alice@gmail.com", "stronkpassword123", "Alice", "Bee")
    return user_ab

@pytest.fixture
def make_user_cd():
    user_cd = auth_register("charlie@gmail.com", "comp1531pass", "Charlie", "Dee")
    return user_cd

@pytest.fixture
def create_public_channel(make_user_ab):
    user_ab = make_user_ab
    channel_id = channels_create(user_ab['token'], 'test_channel_public', True)    
    return (channel_id, user_ab)

@pytest.fixture
def create_private_channel(make_user_ab):
    user_ab = make_user_ab
    channel_id = channels_create(user_ab['token'], 'test_channel_private', False) 
    return (channel_id, user_ab)
    

'''------------------testing message_send--------------------'''
# inputs: (token, channel_id, message); output: {message_id}

# testing if an authorised user who is part of a channel can send messages correctly
# using channel_messages to check 
def test_message_send_correct_output(create_public_channel):
    new_public_channel, user_ab = create_public_channel
    # user_ab sends a message on the public channel
    msg1 = message_send(user_ab['token'], new_public_channel['channel_id'], "Hello world!")
    msg_view = channel_messages(user_ab['token'], new_public_channel['channel_id'], 0)
    first_msg = msg_view['messages'][0]     # dictionary; msg_view is a dictionary of list of dictionaries

    assert first_msg['message_id'] == msg1['message_id']
    assert first_msg['u_id'] == user_ab['u_id']
    assert first_msg['message'] == 'Hello world!'


# check type of message_id to be int and that user messages' message_id's are unique 
def test_message_send_type_id(create_public_channel):
    new_public_channel, user_ab = create_public_channel
    # user_ab sends a message on the public channel
    msg1 = message_send(user_ab['token'], new_public_channel['channel_id'], "Message1")
    msg2 = message_send(user_ab['token'], new_public_channel['channel_id'], "Message2")

    assert type(msg1['message_id']) == type(msg2['message_id']) == int
    assert msg1['message_id'] != msg2['message_id']


# testing that duplicate messages (messages with identical strings) are processed correctly
def test_message_send_duplicate_msgs(create_public_channel, make_user_cd):
    new_public_channel, user_ab = create_public_channel
    user_cd = make_user_cd
    # user_cd joins the channel 
    channel_join(user_ab['token'], new_public_channel['channel_id'])
    msg1_ab = message_send(user_ab['token'], new_public_channel['channel_id'], "I am part of this channel")
    msg2_cd = message_send(user_cd['token'], new_public_channel['channel_id'], "I am part of this channel")
    # retrieving messages
    msgs_view = channel_messages(user_ab['token'], new_public_channel['channel_id'], 0)
    first_msg = msgs_view['messages'][0]
    second_msg = msgs_view['messages'][1]

    assert first_msg['message'] == second_msg['message']
    assert first_msg['message_id'] != second_msg['message_id']
    

# testing that messages of any length (from 0 to 1000 characters) are allowed but any longer strings will throw InputError
# 1. messages with white space and symbols, as long as length is under 1000 characters
def test_message_send_msg_good(create_public_channel):
    new_public_channel, user_ab = create_public_channel
    msg1 = message_send(user_ab['token'], new_public_channel['channel_id'], "awf;lk#5)(*#&                #W*%*@#&(hi")
    msg2 = message_send(user_ab['token'], new_public_channel['channel_id'], "m" * 1000)
    msgs_view = channel_messages(user_ab['token'], new_public_channel['channel_id'], 0)
    # checking that all the above messages sent successfully
    assert len(msgs_view['messages']) == 2


# testing for InputError when message length exceeds 1000 characters
# 1. All symbols
# 2. All white spaces
# 3. a mixture of characters
def test_message_send_msg_bad_symbols(create_public_channel): 
    new_public_channel, user_ab = create_public_channel
    with pytest.raises(InputError):
        message_send(user_ab['token'], new_public_channel['channel_id'], "b" * 1001)

def test_message_send_msg_bad_spaces(create_public_channel): 
    new_public_channel, user_ab = create_public_channel
    with pytest.raises(InputError):
        message_send(user_ab['token'], new_public_channel['channel_id'], " " * 1001)

def test_message_send_msg_bad_message(create_public_channel): 
    new_public_channel, user_ab = create_public_channel
    with pytest.raises(InputError):
        message_send(user_ab['token'], new_public_channel['channel_id'], "message&3." * 500 + " " * 400 + "loong" * 50)


# testing for AccessError: when user is not part of a channel 
def test_message_send_not_part_of_channel(create_private_channel, make_user_cd):
    # user_ab creates a private channel but does not add user_cd to it
    new_private_channel, user_ab = create_private_channel
    user_cd = make_user_cd

    with pytest.raises(AccessError):
        message_send(user_cd['token'], new_private_channel['channel_id'], "fomo")


# testing for AccesError: when previous user/owner of channel leaves the channel and attempts to send message
def test_message_send_owner_removed_send(create_private_channel, make_user_cd):
    new_private_channel, user_ab = create_private_channel
    user_cd = make_user_cd
    # user_ab ads user_cd to the channel
    channel_invite(user_ab['token'], new_private_channel['channel_id'], user_cd['u_id'])
    # user_ab then leaves the channel
    channel_leave(user_ab['token'], new_private_channel['channel_id'])
    
    with pytest.raises(AccessError):
        message_send(user_ab['token'], new_private_channel['channel_id'], "I left")


# testing for Exception: when channel_id is invalid and the channel does not actually exist
def test_message_send_channel_not_found(make_user_ab):
    user_ab = make_user_ab

    with pytest.raises(Exception):
        message_send(user_ab['token'], 22222, "Hello world!")


# testing that empty strings as messages throws exception
# assuming empty strings are bad
def test_message_send_empty_string_bad(create_public_channel): 
    new_public_channel, user_ab = create_public_channel

    with pytest.raises(Exception):
        message_send(user_ab['token'], new_public_channel['channel_id'], "")


# testing that invalid token throws exception
# assuming token with string 'invalid' is an invalid token
def test_message_send_invalid_token(create_public_channel):
    new_public_channel, user_ab = create_public_channel

    with pytest.raises(Exception):
        message_send("invalid", new_public_channel['channel_id'], "Bad message")

'''------------------testing message_remove--------------------'''
# no errors
# testing that owner of channel can remove their own message 
def test_message_remove_owner_remove_own(create_public_channel):
    new_public_channel, user_ab = create_public_channel
    msg1 = message_send(user_ab['token'], new_public_channel['channel_id'], "Hello world!")
    msg2 = message_send(user_ab['token'], new_public_channel['channel_id'], "Second message to channel")
    # now there are two messages; user_ab deletes one of their own
    message_remove(user_ab['token'], msg2['message_id'])
    msgs_view = channel_messages(user_ab['token'], new_public_channel['channel_id'], 0)

    assert len(msgs_view['messages']) == 1

# testing that a member of channel added by the owner is able to remove their own message
def test_message_remove_user_remove_own(create_private_channel, make_user_cd):
    new_private_channel, user_ab = create_private_channel
    user_cd = make_user_cd
    msg1 = message_send(user_ab['token'], new_private_channel['channel_id'], "Please do not post stupid things here")
    # user_ab invites user_cd to private channel
    channel_invite(user_ab['token'], new_private_channel['channel_id'], user_cd['u_id'])
    msg2 = message_send(user_cd['token'], new_private_channel['channel_id'], "Bananas eat monkeys")
    message_remove(user_cd['token'], msg2['message_id'])
    msg3 = message_send(user_ab['token'], new_private_channel['channel_id'], "Thank you.")
    # there should now be 2 messages remaining
    msgs_view = channel_messages(user_ab['token'], new_private_channel['channel_id'], 0)

    assert len(msgs_view['messages']) == 2


# testing that owner of channel can remove message of other users 
# also testing with more messages
def test_message_remove_owner_remove_user_msg(create_public_channel, make_user_cd):
    new_public_channel, user_ab = create_public_channel
    user_cd = make_user_cd
    msg1 = message_send(user_ab['token'], new_public_channel['channel_id'], "Hello world!")
    msg2 = message_send(user_ab['token'], new_public_channel['channel_id'], "Welcome to my channel.")
    msg3 = message_send(user_ab['token'], new_public_channel['channel_id'], "Please do not leave inappropriate messages.")
    msg4 = message_send(user_cd['token'], new_public_channel['channel_id'], "Inappropriate messages.")
    # user_ab (creator of channel) removes message made by user_cd
    message_remove(user_ab['token'], msg4['message_id'])
    msgs_view = channel_messages(user_ab['token'], new_public_channel['channel_id'], 0)

    assert len(msgs_view['messages']) == 3


# InputError (when message_id invalid)
# a previously removed message 
def test_message_remove_nolonger_exist_id(create_public_channel):
    new_public_channel, user_ab = create_public_channel
    msg1 = message_send(user_ab['token'], new_public_channel['channel_id'], "Removing the same message twice.")
    # storing msg1 ID for later reference
    temp_msg1_id = msg1['message_id']
    message_remove(user_ab['token'], msg1['message_id'])

    with pytest.raises(InputError):
        message_remove(user_ab['token'], temp_msg1_id)


# attempting to remove messages with ID of 22222, -1, etc. (assuming these are invalid ID for messages)
def test_message_remove_invalid_id(create_public_channel):
    new_public_channel, user_ab = create_public_channel
    msg1 = message_send(user_ab['token'], new_public_channel['channel_id'], "Hello world!")

    with pytest.raises(InputError):
        message_remove(user_ab['token'], 22222)

    with pytest.raises(InputError):
        message_remove(user_ab['token'], -1) 


# AccessError
# owner of channel removed as owner, tries to remove messages (now as user)
def test_message_remove_old_owner(create_public_channel, make_user_cd):
    new_public_channel, user_ab = create_public_channel
    user_cd = make_user_cd
    channel_addowner(user_ab['token'], new_public_channel['channel_id'], user_cd['u_id'])
    msg1 = message_send(user_cd['token'], new_public_channel['channel_id'], "Good luck deleting this message.")
    # user_cd (now owner) removes user_ab as owner
    channel_removeowner(user_cd['token'], new_public_channel['channel_id'], user_ab['token'])

    with pytest.raises(AccessError):
        message_remove(user_cd['token'], msg1['message_id']) 


# user of channel attempts to remove a message
def test_message_remove_user_remove_msg(create_public_channel, make_user_cd):
    new_public_channel, user_ab = create_public_channel
    user_cd = make_user_cd
    user_ef = auth_register("elephant@gmail.com", "pinkelephant1", "Ele", "Fant")
    # user_ab and user_ef send messages to the channel
    msg1 = message_send(user_ab['token'], new_public_channel['channel_id'], "Hello Elephant!")
    msg2 = message_send(user_ef['token'], new_public_channel['channel_id'], "Hello owner!")
    # checking that AccessError will be thrown when user_cd tries to delete either message
    with pytest.raises(AccessError):
        message_remove(user_cd['token'], msg1['message_id'])

    with pytest.raises(AccessError):
        message_remove(user_cd['token'], msg2['message_id'])
        
# testing that invalid token throws exception
# assuming token with string 'invalid' is an invalid token
def test_message_remove_invalid_token(create_public_channel):
    new_public_channel, user_ab = create_public_channel
    # user_ab and user_ef send messages to the channel
    msg1 = message_send(user_ab['token'], new_public_channel['channel_id'], "Hello Elephant!")

    with pytest.raises(Exception):
        message_remove("invalid", msg1['message_id'])

'''------------------testing message_edit--------------------'''
# updates the text of a message with new text
# if new message is empty string, then new message is deleted
# access error if message-id not sent by correct user: authorised user or admin or owner of channel or slackr

def test_message_edit_one_member_channel(create_public_channel):
    new_ch, user_ab = create_public_channel # user_ab has a u_id and token is the owner of channel_id
    msg_id = message_send(user_ab["token"], new_ch["channel_id"], "First message.")
    
    message_edit(user_ab["token"], msg_id, "Edited first message")
    assert search(user_ab["token"], "Edited first message")["messages"][0]["message"] == \
        "Edited first message"

def test_message_edit_whitespaces(create_public_channel):
    new_ch, user_ab = create_public_channel
    msg_id = message_send(user_ab["token"], new_ch["channel_id"], "First message.")

    message_edit(user_ab["token"], msg_id, "     ")
    assert search(user_ab["token"], "     ")["messages"][0]["message"] == \
        "     "

def test_message_edit_empty(create_public_channel):
    new_ch, user_ab = create_public_channel # user_ab has a u_id and token is the owner of channel_id
    msg1_id = message_send(user_ab["token"], new_ch["channel_id"], "First message.")
    msg2_id = message_send(user_ab["token"], new_ch["channel_id"], "Second message.")
    
    message_edit(user_ab["token"], msg2_id, "Edited second message")
    message_edit(user_ab["token"], msg1_id, "") # should delete the first message

    assert search(user_ab["token"], "message")["messages"][0]["message"] == \
        "Edited second message"

# non-owner sender edits own message
def test_message_edit_sender_edit_self(create_public_channel, make_user_cd):
    new_ch, user_ab = create_public_channel
    user_cd = make_user_cd
    channel_join(user_cd["token"], new_ch["channel_id"])

    msg_id = message_send(user_cd["token"], new_ch["channel_id"], "This is the sender's message.")
    message_edit(user_cd["token"], msg_id, 
                 "This is the sender's message, and now the sender has edited it.")
    
    assert search(user_ab["token"], "message")["messages"][0]["message"] == \
        "This is the sender's message, and now the sender has edited it."

# owner edits sender's message
def test_message_edit_owner_edits_another_sender(create_public_channel, make_user_cd):
    new_ch, user_ab = create_public_channel
    user_cd = make_user_cd
    channel_join(user_cd["token"], new_ch["channel_id"])

    msg_id = message_send(user_cd["token"], new_ch["channel_id"], "This is the sender's message.")
    message_edit(user_ab["token"], msg_id, 
                 "This is the sender's message, and now the owner has edited it.")
    
    assert search(user_ab["token"], "message")["messages"][0]["message"] == \
        "This is the sender's message, and now the owner has edited it."

# Access Error: edit from non-owner, non-sender
def test_message_edit_unauthorised(create_public_channel, make_user_cd):
    new_ch, user_ab = create_public_channel
    user_cd = make_user_cd
    channel_join(user_cd["token"], new_ch["channel_id"])

    msg_id = message_send(user_ab["token"], new_ch["channel_id"], "Owner message")

    with pytest.raises(AccessError):
        message_edit(user_cd["token"], msg_id, "This should be an invalid edit")

# Access Error: general invalid token test
def test_message_edit_invalid_token(create_public_channel):
    new_ch, user_ab = create_public_channel

    msg_id = message_send(user_ab["token"], new_ch["channel_id"], "First message")

    with pytest.raises(AccessError):
        message_edit(user_ab["token"] + "invalid", msg_id, "This is an invalid edit")


# when an owner leaves a channel, they can no longer edit messages in that channel
def test_message_edit_owner_left_channel_invalid(create_public_channel, make_user_cd):
    new_ch, user_ab = create_public_channel
    user_cd = make_user_cd
    channel_join(user_cd["token"], new_ch["channel_id"])
    channel_addowner(user_ab["token"], new_ch["channel_id"], user_cd["u_id"])

    msg_id = message_send(user_cd["token"], new_ch["channel_id"], "Second owner message")

    channel_removeowner(user_cd["token"], new_ch["channel_id"], user_ab["u_id"])

    with pytest.raises(AccessError):
        message_edit(user_ab["token"], msg_id, "First owner should no longer be able to edit others' messages")