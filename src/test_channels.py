#please edit this file for channels functions
# TODO: import functions from other modules if needed
import pytest
import channels
from error import InputError


# Creating users
# These users will be used for testing unless if more are added
user_alice = auth_register("alice@gmail.com", "123456", "Alice", "Bee")
user_charlie = auth_register("charlie@gmail.com", "ABCDEF", "Charlie", "Dragon")

'''------------------testing channels_list--------------------'''

# Testing whether channels_list returns empty list if no channels exist yet
def test_channels_no_channels(): 
    # Assuming users are not part of any channel after registration
    assert channels_list(user_alice['token']) == []

# Testing that channels_list only returns a channel if the user is part of it
def test_channels_part_of_channel():
    # Creating a public channel
    channel_id = channels_create(user_alice['token'], 'channel_0', True)
    assert channels_list(user_alice['token']) == [{'channel_id': channel_id, 'name': 'channel_0'}]
    assert channels_list(user_charlie['token']) == []

'''------------------testing channels_listall--------------------'''



'''------------------testing channels_create--------------------'''