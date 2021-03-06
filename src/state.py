'''
State variables and functions to deal
with the server's data when its launched
'''
#pylint: disable=trailing-whitespace
#pylint: disable=too-many-lines

from email.message import EmailMessage
import threading
import pickle
import random
import uuid
import smtplib
import hashlib
from error import InputError, AccessError

# a constant to show a user is an admin
ADMIN = 1
# a constant to show a user is a regular member
MEMBER = 2
# a constant defining the size of a message block
MSG_BLOCK = 50
# A LOCK for concurrently updating the database
DATABASE_LOCK = threading.Lock()

# needed for generating the image_url
ROUTE = '/imgurl'
HOST = 'http://127.0.0.1'
IMAGE_DIR = './images'
PORT = 5000


def is_this_user_reacted(u_id, link_info):
    '''
    Updates whether the user has reacted given a link which contains message info
    Output: a link_info which has been updated with a new key added to one of its dictionaries
    '''
    # updating is_this_user_reacted based on the authorized user
    reacts_lists = [msg['reacts'] for msg in link_info]

    for reacts_list in reacts_lists:
        for react in reacts_list:
            react['is_this_user_reacted'] = u_id in react['u_ids']


def generate_reset_code():
    '''
    Generate a reset_code to reset a user's password
    Input: None
    Returns: Reset_code
    '''
    # String length ranges from 8 to 10 characters
    str_len = random.randint(8, 10)

    # Generate a unique and secure reset code
    reset_code = uuid.uuid4().hex
    reset_code = reset_code.upper()[0:str_len]
    return reset_code

class Users():
    '''
    A class that contains and manages user information, excluding the links between those users
    and the channels and messages related to them.

    Attributes:
    -----------
    _users : list
        Contains dictionaries with information regarding each user, each dictionary
            contains keys for email, first and last names, pswrd, handle and img_path
    _num_users: int
        Keeps track of the total number of users currently existing
    current_id: int
        Keeps track of the current ID of the latest user. ID's increment by 1 and
            continue to do so even with deletion of previous messages


    '''

    def __init__(self):
        self._users = dict()
        self._num_users = 0
        self._current_id = 0
        self._img_dir = IMAGE_DIR

    def add(self, details):
        '''
        adds user with given details to the database
        Arguments: first and last names, email, password, handle and permissions
        Returns: None
        Raises: InputError, AccessError
        '''
        email, password, f_name, l_name, handle = details

        if self.email_used(email):
            raise InputError("Email already used")

        self._num_users += 1
        self._current_id += 1
        self._users[self._current_id] = {
            'email': email,
            'name_first': f_name,
            'name_last': l_name,
            'password': password,
            'handle_str': handle,
            'img_path': ""
        }
        return self._current_id

    def remove(self, u_id):
        '''
        Remove details of a user with u_id from the dictionary
        '''
        self._users.pop(u_id)
        self._num_users -= 1

    def user_details(self, u_id):
        '''
        Produce a dictionary with the required keys for detail in
        '''
        if not self.user_exists(u_id):
            raise InputError('User does not exist')

        details = self._users[u_id]
        global PORT  # pylint: disable=global-statement
        return {
            'u_id': u_id,
            'email': details['email'],
            'name_first': details['name_first'],
            'name_last': details['name_last'],
            'handle_str': details['handle_str'],
            'profile_img_url': f"{HOST}:{PORT}{ROUTE}?path={details['img_path']}"
                               if details['img_path'] else ""
        }

    def all(self):
        '''
        Returns a list of all users in the specified dictionary format
        '''
        all_users = dict(self._users)
        return list(map(self.user_details, all_users))

    def user_exists(self, u_id):
        '''
        Input: u_id: int
        Returns: Bool
        Checks whether the user with u_id exists
        '''
        if u_id in self._users:
            return True
        return False

    def email_used(self, email):
        '''
        Input: email: string
        Returns: Bool
        Checks whether the email is registered in the database
        '''
        if email in [user['email'] for user in self._users.values()]:
            return True
        return False

    def find_u_id(self, email):
        '''
        Input: email: string
        Returns: u_id: int, None if not found
        Returns the user id given the email if it exists
        '''
        u_id = 1
        for user in self._users.values():
            if email == user['email']:
                return u_id
            u_id += 1

        return None

    def handle_unique(self, handle):
        '''
        Input: handle: string
        Returns: Bool
        Checks if the handle is not already used by another user
        '''
        if handle in [user['handle_str'] for user in self._users.values()]:
            return False

        return True

    def set_first_name(self, u_id, name):
        '''
        Input: u_id: int, name: string
        Returns: nothing
        Resets the first name of user with u_id
        '''
        self._users[u_id]['name_first'] = name

    def set_last_name(self, u_id, name):
        '''
        Input: u_id: int, name: string
        Returns: nothing
        Resets the last name of user with u_id
        '''
        self._users[u_id]['name_last'] = name

    def get_handle(self, u_id):
        '''
        Input: u_id: int
        Returns: handle: string
        Gives back the handle of the user with u_id
        '''
        return self._users[u_id]['handle_str']

    def set_handle(self, u_id, handle_str):
        '''
        Input: u_id: int, handle_str: string
        Returns: nothing
        Resets the handle of user u_id with handle_str
        '''
        self._users[u_id]['handle_str'] = handle_str

    def set_email(self, u_id, email):
        '''
        Input: u_id: int, email: string
        Returns: nothing
        Resets the email of user u_id with new email
        '''
        self._users[u_id]['email'] = email

    def set_password(self, u_id, password):
        '''
        Input: u_id: int, password: string
        Returns: nothing
        Resets the password of user u_id with an encrypted `password`
        '''
        encrypt_pass = hashlib.sha256(password.encode()).hexdigest()
        self._users[u_id]['password'] = encrypt_pass

    def set_image(self, u_id):
        '''
        Input: u_id: int
        Returns: nothing
        Creates an img path using u_id and saves it into the user's details
        '''
        self._users[u_id]['img_path'] = f"{self._img_dir}/{u_id}.jpg"

    def validate_login(self, email, password):
        '''
        Input: email: string, password: string
        Returns: u_id of the validated user
        Makes sure the email exist and the given password is correct
        '''
        try:
            [u_id] = [
                key for key,
                value in self._users.items() if value['email'] == email]
        except ValueError:
            raise InputError('Email does not exist')

        if password != self._users[u_id]['password']:
            raise InputError(description='Password incorrect')
        return u_id


class Admins():
    '''
    A special class for users who are admins
    '''

    def __init__(self):
        self._admins = list()
        self._valid_permissions = [ADMIN, MEMBER]

    def add(self, u_id):
        '''
        Input: u_id: int
        Returns: Nothing
        Purpose: add the u_id into the admins list
        '''
        if not self.is_admin(u_id):
            self._admins.append(u_id)

    def remove(self, u_id):
        '''
        Input: u_id: int
        Returns: Nothing
        Purpose: remove the u_id from the admins list
        '''
        if self.is_admin(u_id):
            self._admins.remove(u_id)
# A timer that sends http requests to update database

    def is_admin(self, u_id):
        '''
        Input: u_id (int)
        Return: whether u_id is an admin (bool)
        '''
        return u_id in self._admins

    def is_valid_permission(self, p_id):
        '''
        Input:
            p_id (int): a permission ID
        Return:
            wehther the permission_id is valid (bool)
        '''
        return p_id in self._valid_permissions


class Channels():
    '''
    A class to add newly created channels to the database
    and also gather information about specified channels.
    Also store information about the hangman game within
    each channel
    '''

    def __init__(self):
        self._channels = dict()
        self._num_channels = 0
        self._current_id = 0

    def add(self, details):
        '''
        Adds details of a channel to dictionary
        Input: Channel details
        Output: Channel
        '''
        name, is_public = details

        self._num_channels += 1
        self._current_id += 1
        self._channels[self._current_id] = {
            'name': name,
            'is_public': is_public,
            'hangman': {
                'bot_id': -1,
                'bot_token': 'o',
                'is_enabled': True,
                'is_running': False,
                'data': {
                    # target_word
                    # user_guess
                    # letters_to_guess
                    # lives_remaining
                    # game_end
                    # output
                }
            }
        }
        return self._current_id

    def is_private(self, channel_id):
        '''
        Checks if channel is private
        Input: Channel id
        Returns: False if private
        '''
        return not self._channels[channel_id]['is_public']

    def channel_exists(self, channel_id):
        '''
        Checks if channel_exists
        Input: Channel id
        Returns: Channel_id or None
        '''

        return channel_id in self._channels

    def channel_details(self, channel_id):
        '''
        Raise error if channel doesn't exist otherwise
        return its details
        Input: Channel id
        Returns: Name and channel_id of a specified channel
        '''
        if not self.channel_exists(channel_id):
            raise InputError(description="Channel does not exist")

        details = dict(self._channels[channel_id])
        return {
            'channel_id': channel_id,
            'name': details['name']
        }

    def all(self):
        '''
        Returns a list of all channels created, displaying their details
        '''
        channels_copy = dict(self._channels)
        return list(map(self.channel_details, channels_copy))


# methods relating to hangman game


    def is_hangman_enabled(self, channel_id):
        '''
        Check if hangman game is enabled
        Args: channel_id (int)
        Return: whether hangman is enabled (bool)
        '''
        return bool(self._channels[channel_id]['hangman']['is_enabled'])

    def enable_hangman(self, channel_id):
        '''
        Enables hangman game within channel
        Args: channel_id (int)
        '''
        self._channels[channel_id]['hangman']['is_enabled'] = True

    def disable_hangman(self, channel_id):
        '''
        Disable hangman game within channel
        Args: channel_id (int)
        '''
        self._channels[channel_id]['hangman']['is_enabled'] = False

    def is_hangman_running(self, channel_id):
        '''
        Check if hangman game is running in channel
        Args: channel_id (int)
        Return: whether hangman is running in the channel (bool)
        '''
        return bool(self._channels[channel_id]['hangman']['is_running'])

    def add_hbot_details(self, channel_id, bot_id, bot_token):
        '''
        Adds the hangman bot details to the dictionary when it is created
        Args: channel_id (int), bot_id (int), bot_token (str)
        '''
        self._channels[channel_id]['hangman']['bot_id'] = bot_id
        self._channels[channel_id]['hangman']['bot_token'] = bot_token

    def get_hbot_details(self, channel_id):
        '''
        Given a channel id return details about hangman game bot
        '''
        return (
            self._channels[channel_id]['hangman']['bot_id'],
            self._channels[channel_id]['hangman']['bot_token']
        )

    def start_hangman(self, channel_id, details):
        '''
        Changes the state of hangman in specified channel to True
        And passes in details to dicitonary
        '''
        self._channels[channel_id]['hangman']['is_running'] = True
        # initialising variables to start game
        self._channels[channel_id]['hangman']['data'] = details

    def get_hangman(self, channel_id):
        '''
        Return dictionary of the details of the current hangman game
        '''
        return dict(self._channels[channel_id]['hangman']['data'])

    # for each turn during the ongoing game
    def edit_hangman(self, channel_id, new_details):
        '''
        Updates the details in the hangman database given users' interactions
        with the hangman bot
        '''
        self._channels[channel_id]['hangman']['data'] = new_details

    def quit_hangman(self, channel_id):
        '''
        Clear all data in the hangman dict
        '''
        self._channels[channel_id]['hangman']['data'].clear()
        self._channels[channel_id]['hangman']['is_running'] = False


class Codes():
    '''
    A class to store reset codes in a dictionary with a user's email
    as the key to allow users to reset their passwords
    '''

    def __init__(self):
        self._codes_dict = dict()
        self._num_codes = 0

    def _send_email(self, email):
        sender_email = 'comp1531resetpass@gmail.com'
        sender_pass = 'git_commitment_issues'
        msg = EmailMessage()
        msg['From'] = sender_email
        msg['To'] = email
        msg.set_content(self._codes_dict[email])

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_pass)
            smtp.send_message(msg)

    def push(self, email):
        '''
        Append reset_code to dictionary
        '''
        if email in self._codes_dict:
            self.delete(email)

        reset_code = generate_reset_code()
        self._codes_dict[email] = reset_code
        self._num_codes += 1
        self._send_email(email)

    def delete(self, email):
        '''
        Delete reset code from dicitonary
        '''
        del self._codes_dict[email]
        self._num_codes -= 1

    def code_exists(self, reset_code):
        '''
        Check if given reset code exists within dictionary else raise an error
        '''
        for values in self._codes_dict.values():
            if reset_code in values:
                return True
        raise InputError(description="Reset code is not valid")

    def find_email(self, reset_code):
        '''
        Returns email within codes dictionary if reset code matches one within dicitonary
        else return None
        '''
        return [key for (key, value) in self._codes_dict.items()
                if value == reset_code]


class Messages():
    '''
    A class that contains information about all messages that have been sent into channels,
        including their id, message string, time created and pinned status

    Attributes:
    -----------
    messages : list
        Contains dictionaries with information regarding each message, each dictionary
            contains keys message_id, message, time_created and is_pinned
    num_messages: int
        Keeps track of the total number of messages currently existing
    current_id: int
        Keeps track of the current ID of the latest message sent. ID's increment by 1 and
            continue to do so even with deletion of previous messages

    Methods:
    --------
    def all(self)
    def add(self, details)
    def edit(self, message_id, message)
    def pin(self, message_id)
    def unpin(self, message_id)
    def message_details(self, message_id)
    def message_exists(self, message_id)
    def fetch_messages(self, start)
    def remove(self, message_id)
    def find(self, message_id)
    def search(self, query_string)
    def next_id(self)
    '''

    def __init__(self):
        self._messages = list()
        self._num_messages = 0
        self._current_id = 0

    def all(self):
        '''
        Returns all message dictionaries in a list
        '''
        return list(self._messages)

    def add(self, details):
        '''
        Appends to the list of messages a new dictionary
        containing the following details
        '''
        message, time_created = details
        self._num_messages += 1
        self._current_id += 1
        self._messages.append({
            'message_id': self._current_id,
            'message': message,
            'time_created': time_created,
            'is_pinned': False,
        })
        return self._current_id

    def edit(self, message_id, message):
        '''
        Replaces the contents of message with message_id
        with the message string
        '''
        for msg in self._messages:
            if msg['message_id'] == message_id:
                msg['message'] = message

    def pin(self, message_id):
        '''
        Pins the message with message_id
        '''
        if self.message_details(message_id)['is_pinned']:
            raise InputError(description='Message already pinned')
        ids = [msg['message_id'] for msg in self._messages]
        self._messages[ids.index(message_id)]['is_pinned'] = True

    def unpin(self, message_id):
        '''
        Unpins the message with message_id
        '''
        if not self.message_details(message_id)['is_pinned']:
            raise InputError(description='Message already unpinned')
        ids = [msg['message_id'] for msg in self._messages]
        self._messages[ids.index(message_id)]['is_pinned'] = False

    def message_details(self, message_id):
        '''
        Returns details of message with message_id
        in the form of a dictionary
        '''
        try:
            [message] = list(
                filter(
                    lambda x: x['message_id'] == message_id,
                    self._messages))
            return dict(message)
        except ValueError:
            return None

    def message_exists(self, message_id):
        '''
        Returns whether message with message_id exists
        '''
        return message_id in [message['message_id']
                              for message in self._messages]

    def fetch_messages(self, start):
        '''
        Returns a list of message details starting
        with the specified start index
        '''
        if start < 0 or start > self._num_messages:
            raise InputError(description='Invalid Start index')
        if start + MSG_BLOCK >= self._num_messages:
            return list(self._messages[start:])
        return list(self._messages[start: start + MSG_BLOCK])

    def remove(self, message_id):
        '''
        Removes a message with message_id
        '''
        if not self.message_exists(message_id):
            raise InputError(description='Message does not exist')
        self._messages[:] = list(
            filter(
                lambda x: x['message_id'] != message_id,
                self._messages))
        self._num_messages -= 1

    def find(self, message_id):
        '''
        Returns the message_id of message
        '''
        return self._messages[message_id]

    def search(self, query_string):
        '''
        Returns list of messages that contain the query_string
        '''
        return list(
            [msg for msg in self._messages if query_string in msg['message']])

    def next_id(self):
        '''
        Returns the next message ID
        '''
        return int(self._current_id + 1)


class UserMessage():
    '''
    A class containing the structure that maintains the relationship
    between users, channels, reacts and messages they sent

    Attributes:
    -----------
    user_messages : list
        Contains tuples with information linking message_id to u_id, as well
            as channel_id and creates an empty reacts list of that message
    react_ids: list
        Stores the currently valid react ID's (currently 1)

    Methods:
    --------
    def add_link(self, u_id, channel_id, message_id)
    def fetch_links_by_channel(self, container)
        returns list of links filtered by specified channel_id(s)
    def fetch_links_by_user(self, u_id)
    def remove_link_by_user(self, u_id)
    def remove_link_by_channel(self, channel_id)
    def remove_link_by_message(self, message_id)
    def link_exists(self, message_id)
    def react(self, u_id, m_id, react_id)
    def unreact(self, u_id, m_id, react_id)
    def fetch_link(self, m_id)
        returns the tuple containing a specified message_id
    def is_valid_react(self, react_id)
    def is_sender(self, m_id, u_id)
    def message_channel(self, message_id)
        returns the channel the message with message_id is in
    '''

    def __init__(self):
        self._user_messages = list()
        self._react_ids = [1]

    def add_link(self, u_id, channel_id, message_id):
        '''
        Adds a tuple containing u_id, channel_id, message_id
        '''
        if self.link_exists(message_id):
            raise InputError(description='Message already exists')
        self._user_messages.append({
            'message_id': message_id,
            'u_id': u_id,
            'channel_id': channel_id,
            'reacts': [{
                'react_id': 1,
                'u_ids': []
            }]
        })

    def fetch_links_by_channel(self, container):
        '''
        Fetches all links by channel_id/multiple channel_ids
        '''
        if isinstance(container, list):
            channel_msgs = list(
                filter(
                    lambda x: x['channel_id'] in container,
                    self._user_messages))
        else:
            channel_msgs = list(
                filter(
                    lambda x: x['channel_id'] == container,
                    self._user_messages))

        return list(channel_msgs)

    def fetch_links_by_user(self, u_id):
        '''
        Fetches all message links that the user has sent
        '''
        filtered = list(
            filter(
                lambda x: x['u_id'] == u_id,
                self._user_messages))
        return list(filtered)

    def remove_link_by_user(self, u_id):
        '''
        Removes all tuples from list of links containing u_id
        '''
        self._user_messages = list(
            filter(
                lambda x: x['u_id'] != u_id,
                self._user_messages))

    def remove_link_by_channel(self, channel_id):
        '''
        Removes all tuples from list of links containing channel_id
        '''
        self._user_messages = list(
            filter(lambda x: x['channel_id'] != channel_id, self._user_messages))

    def remove_link_by_message(self, message_id):
        '''
        Removes all tuples from list of links containing channel_id
        '''
        self._user_messages = list(
            filter(lambda x: x['message_id'] != message_id, self._user_messages))

    def link_exists(self, message_id):
        '''
        Checks whether a tuple with message_id exists in user_messages
        '''
        return message_id in [link['message_id']
                              for link in self._user_messages]

    def react(self, u_id, m_id, react_id):
        '''
        Adds react details to the link with u_id, m_id
        '''
        if not self.link_exists(m_id):
            raise InputError(description='Message does not exist')

        if not self.is_valid_react(react_id):
            raise InputError(description='Invalid react')

        [link] = list(
            filter(lambda x: x['message_id'] == m_id, self._user_messages))

        reacts = link['reacts']

        try:
            react = None
            for tmp_react in reacts:
                if tmp_react['react_id'] == react_id:
                    react = tmp_react
            if u_id in react['u_ids']:
                raise InputError(description='user already reacted')
            react['u_ids'].append(u_id)
        except (ValueError, TypeError):
            reacts.append({
                'react_id': react_id,
                'u_ids': [u_id],
            })

    def unreact(self, u_id, m_id, react_id):
        '''
        Removes the react_id from active reacts in the specified link
        '''
        if not self.link_exists(m_id):
            raise InputError(description='Message does not exist')

        if not self.is_valid_react(react_id):
            raise InputError(description='Invalid react')

        [link] = list(
            filter(lambda x: x['message_id'] == m_id, self._user_messages))

        reacts = link['reacts']
        try:
            [react] = list(filter(lambda x: x['react_id'] == react_id, reacts))
            react['u_ids'].remove(u_id)
        except ValueError:
            raise InputError(description='user does not have an active react')

    def fetch_link(self, m_id):
        '''
        Returns the link tuple containing message ID of m_id
        '''
        try:
            [info] = list(
                filter(
                    lambda x: x['message_id'] == m_id,
                    self._user_messages))
            return info
        except ValueError:
            return None

    def is_valid_react(self, react_id):
        '''
        Checks whether the react_id is valid
        '''
        return react_id in self._react_ids

    def is_sender(self, m_id, u_id):
        '''
        Checks whether the user with ID u_id sent the message with m_id
        '''
        return u_id in [link['u_id']
                        for link in self._user_messages if link['message_id'] == m_id]

    def message_channel(self, message_id):
        '''
        Returns the channel ID of the message
        '''
        link = self.fetch_link(message_id)
        return link['channel_id']


class UserChannel():
    '''
    A class that maintains the relationship between users and the channels they have joined.

    Attributes:
    -----------
    user_channels : list
        Contains tuples linking u_id's to channel_id's, as well as
        whether the user with u_id is an owner of that channel

    Methods:
    --------
    add_link(u_id, channel_id, is_owner)
        links a 'u_id' to a 'channel_id', adding whether the user is an owner of that channel
    remove_link_by_user(u_id)
        removes all links between channels and user with 'u_id'
    remove_link_by_channel(channel_id)
        removes all links between users and channel with 'channel_id'
    remove_user(u_id, channel_id)
        removes user with 'u_id' from channel with 'channel_id'
    add_owner(u_id, channel_id)
        adds user with 'u_id' to the list of owners for channel with 'channel_id'
    remove_owner(u_id, channel_id)
        removes user with 'u_id' from the list of owners for channel with 'channel_id'
    join_channel(u_id, channel_id)
        adds user with 'u_id' to channel with 'channel_id' as a normal member
    leave_channel(u_id, channel_id)
        removes user with 'u_id' from channel with 'channel_id' entirely
    link_exists(self, u_id, channel_id)
        returns whether user with 'u_id' is part of channel with 'channel_id'
    is_member(self, u_id, channel_id)
        returns whether user with 'u_id' is a normal member of channel with 'channel_id'
    is_owner(self, u_id, channel_id)
        returns whether user with 'u_id' is an owner of channelw ith 'channel_id'
    members(self, channel_id)
        returns a list of all members part of channel with 'channel_id'
    owners(self, channel_id)
        returns a list of all owner members in channel with 'channel_id'
    user_channels(self, given_u_id)
        returns a list of channels which user with 'given_u_id' is part of
    '''

    def __init__(self):
        self._user_channels = list()

    def add_link(self, u_id, channel_id, is_owner):
        '''
        Forms a link between a user and a channel, making a note of
        whether the user is an owner of that channel.

        Params: u_id (int), channel_id (int), is_owner (bool)
        Raises: InputError if user is already in the channel
        '''
        if self.link_exists(u_id, channel_id):
            raise InputError(description='user already in channel')

        self._user_channels.append((u_id, channel_id, is_owner))

    def remove_link_by_user(self, u_id):
        '''
        Removes a link made between a user with 'u_id' and all chanenels this user is part of

        Params: u_id (int)
        '''
        self._user_channels = list(
            filter(
                lambda x: x[0] != u_id,
                self._user_channels))

    def remove_link_by_channel(self, channel_id):
        '''
        Removes a link made between a channel with 'channel_id' and all users part of this channel

        Params: channel_id (int)
        '''
        self._user_channels = list(
            filter(
                lambda x: x[1] != channel_id,
                self._user_channels))

    def remove_user(self, u_id, channel_id):
        '''
        Removes user with 'u_id' from channel with 'channel_id'

        Params: u_id (int), channel_id (int)
        Raises: ValueError if either 'u_id' or 'channel_id' invalid or user not part of channel
        '''
        try:
            [to_remove] = list(
                filter(lambda x: x[0] == u_id and x[1] == channel_id, self._user_channels))
            self._user_channels.remove(to_remove)
        except ValueError:
            pass

    def add_owner(self, u_id, channel_id):
        '''
        Adds user with 'u_id' to the list of owners for channel with 'channel_id'

        Params: u_id (int), channel_id (int)
        Raises: InputError if user is already an owner of the channel
        '''
        if self.is_owner(u_id, channel_id):
            raise InputError(description='user is already an owner')
        # tuples cannot allow modification; therefore delete then add
        self.remove_user(u_id, channel_id)
        self.add_link(u_id, channel_id, is_owner=True)

    def remove_owner(self, u_id, channel_id):
        '''
        Removes user with 'u_id' from the list of owners for channel with 'channel_id'

        Params: u_id (int), channel_id (int)
        Raises: InputError if user is not an owner of the channel in the first place
        '''
        if not self.is_owner(u_id, channel_id):
            raise InputError(description='user is not an owner')

        # tuples are immutable; so we delete him then add him as a member
        self.remove_user(u_id, channel_id)
        self.add_link(u_id, channel_id, is_owner=False)

    def join_channel(self, u_id, channel_id):
        '''
        Adds user with 'u_id' to channel with 'channel_id' as a normal member

        Params: u_id (int), channel_id (int)
        '''
        self.add_link(u_id, channel_id, is_owner=False)

    def leave_channel(self, u_id, channel_id):
        '''
        Removes user with 'u_id' from channel with 'channel_id' entirely

        Params: u_id (int), channel_id (int)
        '''
        self.remove_user(u_id, channel_id)

    def link_exists(self, u_id, channel_id):
        '''
        Params: u_id (int), channel_id (int)
        Returns: if user is part of channel (bool)
        '''
        return u_id in \
            [u_id for u_id, ch_id, _ in self._user_channels if ch_id == channel_id]

    def is_member(self, u_id, channel_id):
        '''
        Params: u_id (int), channel_id (int)
        Returns: if user is normal member of channel (bool)
        '''
        return u_id in self.members(channel_id)

    def is_owner(self, u_id, channel_id):
        '''
        Params: u_id (int), channel_id (int)
        Returns: if user is owner member of channel (bool)
        '''
        return u_id in self.owners(channel_id)

    def members(self, channel_id):
        '''
        Params: channel_id (int)
        Returns: all users who are normal members of channel with 'channel_id' (List)
        '''
        return [u_id for u_id, ch_id,
                _ in self._user_channels if channel_id == ch_id]

    def owners(self, channel_id):
        '''
        Params: channel_id (int)
        Returns: all users who are owner members of channel with 'channel_id' (List)
        '''
        return [u_id for u_id, ch_id, is_owner in self._user_channels if
                ch_id == channel_id and is_owner]

    def user_channels(self, given_u_id):
        '''
        Params: given_u_id (int)
        Returns: all channels which user with 'given_u_id' is part of (List)
        '''
        return list(
            [ch_id for u_id, ch_id, _ in self._user_channels if u_id == given_u_id])


class Database():
    '''
    A class which acts as a centralised base-point from which to access methods
    that edit or report from the database.

    Attributes:
    -----------
    users: class
    admins: class
    channels: class
    codes: class
    messages: class
    user_message: class
    user_channel: class

    Methods:
    --------
    reset()
        Reinitialises the database
    add_user(details)
        Adds a user with 'details' to the database
    user_channels(u_id)
        Returns details of all the channels user is in
    add_channel(u_id, details)
        Adds a channel to the database,
        rendering the user who created it its owner
    channel_members(channel_id)
        Returns information on all normal members in a channel
    channel_owners(channel_id)
        Returns information on all owner members in a channel
    channel_messages(u_id, details)
        Returns up to 50 messages from a channel
    add_message(u_id, channel_id, details)
        Adds a message sent by user with 'u_id' to channel with 'channel_id'
    remove_message(message_id)
        Removes a message with 'message_id'
    message_search(u_id, query_str)
        Searches channels which user with 'u_id' is part of
        for messages which contain the query_str
    remove_messages(u_id)
        Removes all messages associated with a user
    pin(u_id, message_id)
        Marks a message for special treatment in the frontend
    unpin(u_id, message_id)
        Unmarks a message for special treatment in the frontend

    '''

    def __init__(self):
        self.users = Users()
        self.admins = Admins()
        self.channels = Channels()
        self.codes = Codes()
        self.messages = Messages()
        self.user_message = UserMessage()
        self.user_channel = UserChannel()

    def reset(self):
        '''Reinitialises the database'''
        self.__init__()

    def add_user(self, details):
        '''
        Adds a user with 'details' to the database

        Args:
            details (tuple): containing email (str), encrypted password (str),
                name_first (str), name_last (str), handle (str)
        Return: u_id (int)
        '''
        u_id = self.users.add(details)
        # first user is an admin
        if u_id == 1:
            self.admins.add(u_id)
        return u_id

    def user_channels(self, u_id):
        '''
        Returns details of all the channels user is in

        Args: u_id (int)
        Return: list of dictionaries each containing
            channel_id (int)
            name (str): of channel
        '''
        channels = self.user_channel.user_channels(u_id)
        details = list(map(self.channels.channel_details, channels))
        return list(details)

    def add_channel(self, u_id, details):
        '''
        Adds a channel to the database,
        rendering the user who created it its owner

        Args:
            u_id (int)
            details (tuple): name of channel (str), is_public (bool)
        Return:
            channel_id (int)
        '''
        channel_id = self.channels.add(details)
        self.user_channel.add_link(u_id, channel_id, is_owner=True)
        return channel_id

    def channel_members(self, channel_id):
        '''
        Returns information on all normal members in a channel

        Args: channel_id (int)
        Return: list of dictionaries each containing info about a user:
            u_id (int), name_first (str), name_last (str), profile_img_url (str)
        '''
        member_ids = self.user_channel.members(channel_id)
        members_info = list(map(self.users.user_details, member_ids))
        return list([{
            'u_id': member['u_id'],
            'name_first':member['name_first'],
            'name_last': member['name_last'],
            'profile_img_url': member['profile_img_url']
        } for member in members_info])

    def channel_owners(self, channel_id):
        '''
        Returns information on all owner members in a channel

        Args: channel_id (int)
        Return: list of dictionaries each containing info about a user:
            u_id (int), name_first (str), name_last (str), profile_img_url (str)
        '''
        member_ids = self.user_channel.owners(channel_id)
        members_info = list(map(self.users.user_details, member_ids))
        return list([{
            'u_id': member['u_id'],
            'name_first':member['name_first'],
            'name_last': member['name_last'],
            'profile_img_url': member['profile_img_url']
        } for member in members_info])

    def channel_messages(self, u_id, details):
        '''
        Returns up to 50 messages from a channel

        Args:
            u_id (int): of the user invoking this action
            details (tuple):
                channel_id (int)
                start (int): starting index
        Return:
            List of up to 50 dictionaries each containing:
                message_id (int)
                u_id (int): of the user who sent the message
                message (str)
                time_created (time)
                reacts (List)
                is_pinned (bool)
        '''
        channel_id, start = details
        # getting the links between messages, users and channels
        link_info = self.user_message.fetch_links_by_channel(channel_id)
        # not enough messages to retrieve
        if start > len(link_info):
            raise InputError('Invalid start index')

        # no relevant messages
        if not link_info:
            return [], False  # False means no more messages to return

        # getting message details given the message id
        msgs_info = list(
            map(lambda x: self.messages.message_details(x['message_id']), link_info))

        # updating the is_this_user_reacted field for the reacts
        is_this_user_reacted(u_id, link_info)
        # constructing the full details
        full_info = list(map(lambda x, y: {
            'message_id': y['message_id'],
            'u_id': x['u_id'],
            'message': y['message'],
            'time_created': y['time_created'],
            'reacts': x['reacts'],
            'is_pinned': y['is_pinned']
        }, link_info, msgs_info))

        # sorting based on timestamp
        full_info.sort(key=lambda x: x['time_created'], reverse=True)
        # chopping messages
        if start + MSG_BLOCK < len(full_info):
            # means more to give
            return list(full_info[start: start + MSG_BLOCK]), True
        return list(full_info[start:]), False  # means no more to give

    def add_message(self, u_id, channel_id, details):
        '''
        Adds a message sent by user with 'u_id' to channel with 'channel_id'

        Args:
            u_id (int)
            channel_id (int)
            details (tuple):
                message (str): typed in by the user
                time (time): at which the message was sent
        Return:
            message_id (int): unique identifier of the message within the channel
        '''
        message_id = self.messages.add(details)
        self.user_message.add_link(u_id, channel_id, message_id)
        return message_id

    def remove_message(self, message_id):
        '''
        Removes a message

        Args: message_id (int)
        '''
        self.messages.remove(message_id)
        self.user_message.remove_link_by_message(message_id)

    def message_search(self, u_id, query_str):
        '''
        Searches channels which user with 'u_id' is part of
        for messages which contain the query_str

        Args:
            u_id (int): of the user invoking the function
            query_str (str): which the user requests be contained in the search results
        Return:
            a list of dictionaries each containing information about a message
            that contains the query_str, sorted in numerical order by message_id:
            message_id (int)
                u_id (int): of the user who sent the message
                message (str)
                time_created (time)
                reacts (List)
                is_pinned (bool)
        '''
        # fetching relevant channels
        channel_ids = self.user_channel.user_channels(u_id)
        if not channel_ids:
            return []

        # fetching relevant message links to those channels
        filtered_links = self.user_message.fetch_links_by_channel(channel_ids)
        # getting the relevant message ids
        filtered_mids = list(map(lambda x: x['message_id'], filtered_links))
        # getting all messages with a query string
        msgs = self.messages.search(query_str)
        # filtering those messages based on the message ids
        relevant_msgs = list(
            filter(
                lambda x: x['message_id'] in filtered_mids,
                msgs))
        # updating the is_this_user_reacted key for all the reacts
        is_this_user_reacted(u_id, filtered_links)
        # constructing the full details
        relevant_msgs = list(map(lambda x, y: {
            'message_id': y['message_id'],
            'u_id': x['u_id'],
            'message': y['message'],
            'time_created': y['time_created'],
            'reacts': x['reacts'],
            'is_pinned': y['is_pinned']
        }, filtered_links, relevant_msgs))
        return sorted(
            relevant_msgs, key=lambda x: x['time_created'], reverse=True)

    def remove_messages(self, u_id):
        '''
        Removes all messages associated with a user
        Args: u_id (int)
        '''
        relevant_msg_links = self.user_message.fetch_links_by_user(u_id)
        for link in relevant_msg_links:
            self.remove_message(link['message_id'])

        self.user_message.remove_link_by_user(u_id)

    def pin(self, u_id, message_id):
        '''
        Marks a message for special treatment in the frontend
        Args: u_id (int), message_id (int)
        Raises:
            InputError: if message_id does not correspond to a message that exists
            AccessError: if user with u_id does not have permission to pin
        '''
        # check message exists
        if not self.messages.message_exists(message_id):
            raise InputError(description='Message does not exist')

        # getting the channel_id in which the message was sent
        channel_id = self.user_message.message_channel(message_id)

        # validate the user is an owner or an admin of the channel
        if not self.user_channel.is_owner(
                u_id, channel_id) and not self.admins.is_admin(u_id):
            raise AccessError(
                description='You do not have access to pin message')

        self.messages.pin(message_id)

    def unpin(self, u_id, message_id):
        '''
        Unmarks a message for special treatment in the frontend
        Args: u_id (int), message_id (int)
        Raises:
            InputError: if message_id does not correspond to a message that exists
            AccessError: if user with u_id does not have permission to unpin
        '''
        # checking message exists
        if not self.messages.message_exists(message_id):
            raise InputError(description='Message does not exist')

        # getting the channel_id in which the message was sent
        channel_id = self.user_message.message_channel(message_id)

        # user should be an owner or an admin
        if not self.user_channel.is_owner(
                u_id, channel_id) and not self.admins.is_admin(u_id):
            raise AccessError(
                description='You do not have access to pin message')

        self.messages.unpin(message_id)


STORE = Database()
# this dictionary contains the session tokens that
# won't need to be stored in the Store data dictionary for pickling
# {"token_str1": u_id1, "token_str2": u_id2, ..}
TOKENS = dict()


def image_config():
    '''
    returns all the configurations needed to save and serve images
    '''
    # pylint: disable=global-statement
    global IMAGE_DIR
    global HOST
    global PORT
    global ROUTE
    return {
        'path': IMAGE_DIR,
        'host': HOST,
        'port': PORT,
        'route': ROUTE,
    }


def get_store():
    '''
    Returns the global data structure STORE for modification by other functions
    in other files
    '''
    global STORE  # pylint: disable=global-statement
    return STORE


def get_tokens():
    '''
    Returns the global data structure Tokens for modification by other functions
    in other files
    '''
    global TOKENS  # pylint: disable=global-statement
    return TOKENS


def initialize_store():
    '''
    Initialize the server database dictionary, creates an empty dictionary if the
    database file is empty
    '''
    global STORE  # pylint: disable=global-statement
    with open('database.p', "rb") as file:
        try:
            STORE = pickle.load(file, encoding="utf-8")
        except EOFError:
            STORE = Database()


def initialize_state():
    '''
    initialise the store and the tokens dictionary
    '''
    initialize_store()
    global TOKENS  # pylint: disable=global-statement
    TOKENS = dict()


# A constant to update the database every hour
SECONDS_TO_UPDATE = 3000


def update_database():
    '''
    pickle the state database into a file
    '''
    # pylint: disable=global-statement

    global STORE

    with DATABASE_LOCK:
        with open('database.p', "wb") as database_file:
            pickle.dump(STORE, database_file)
    print('Updated database!')
