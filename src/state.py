'''
State variables and functions to deal
with the server's data when its launched
'''
from threading import Timer, Thread
import pickle

from error import InputError, AccessError

#a constant to show a user is an admin
ADMIN = 1
#a constant to show a user is a regular member
MEMBER = 1
#a constant defining the size of a message block
MSG_BLOCK = 50

class Users():
    def __init__(self):
        self._users = dict()
        self._num_users = 0
        self._current_id = 0
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
            'global_permission': ADMIN if self._num_users == 1 else MEMBER
        }
        return self._current_id

    def remove(self, u_id):
        self._users.pop(u_id)
        self._num_users -= 1
    
    def user_details(self, u_id):
        if not self.user_exists(u_id):
            raise InputError('User does not exist')

        details = self._users[u_id]
        return {
            'u_id': u_id,
            'email': details['email'],
            'name_first': details['name_first'],
            'name_last': details['name_last'],
            'handle_str': details['handle_str'],
        }

    def all(self):
        all_users = dict(self._users)
        return list(map(self.user_details, all_users))

    def user_exists(self, u_id):
        if u_id in self._users:
            return True
        return False

    def email_used(self, email):
        if email in [user['email'] for user in self._users.values()]:
            return True
        return False

    def handle_unique(self, handle):
        if handle in [user['handle_str'] for user in self._users.values()]:
            return False 

        return True 

    def set_first_name(self, u_id, name):
        self._users[u_id]['name_first'] = name

    def set_last_name(self, u_id, name):
        self._users[u_id]['name_last'] = name
    
    def get_handle(self, u_id):
        return self._users[u_id]['handle_str']

    def set_handle(self, u_id, handle_str):
        self._users[u_id]['handle_str'] = handle_str

    def set_email(self, u_id, email):
        self._users[u_id]['email'] = email

    def validate_login(self, email, password):
        try:
            [u_id] = [key for key, value in self._users.items() if value['email'] == email]
        except ValueError:
            raise InputError('Email does not exist')

        if password != self._users[u_id]['password']:
            raise AccessError(description='Password incorrect')
        return u_id

class Admins(Users):
    '''
    A special class for users who are admins
    '''
    def is_admin(self, u_id):
        return u_id in self._users

class Channels():
    def __init__(self):
        self._channels = dict()
        self._num_channels = 0
        self._current_id = 0

    def add(self, details):
        name, is_public = details

        self._num_channels += 1
        self._current_id += 1
        self._channels[self._current_id] = {
            'name': name,
            'is_public': is_public
        }
        return self._current_id

    def is_private(self, channel_id):
        return not self._channels[channel_id]['is_public']

    def channel_exists(self, channel_id):
        return channel_id in self._channels

    def channel_details(self, channel_id):
        if not self.channel_exists(channel_id):
            raise InputError(description="Channel does not exist")

        details = dict(self._channels[channel_id])
        return {
            'channel_id': channel_id,
            'name': details['name']
        }

    def all(self):
        channels_copy = dict(self._channels)
        return list(map(self.channel_details, channels_copy))

class Messages():
    def __init__(self):
        self._messages = list()
        self._num_messages = 0
        self._current_id = 0

    def all(self):
        return list(self._messages)

    def add(self, details):
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
        for msg in self._messages:
            if msg['message_id'] == message_id:
                msg['message'] = message

    def pin(self, message_id):
        if self.message_details(message_id)['is_pinned']:
            raise InputError(description='Message already pinned')
        self.message_details(message_id)['is_pinned'] = True

    def unpin(self, message_id):
        if not self.message_details(message_id)['is_pinned']:
            raise InputError(description='Message already unpinned')
        self.message_details(message_id)['is_pinned'] = False

    def message_details(self, message_id):
        try:
            [message] = list(filter(lambda x: x['message_id'] == message_id, self._messages))
            return dict(message)
        except ValueError:
            return None

    def message_exists(self, message_id):
        return message_id in [message['message_id'] for message in self._messages]

    def fetch_messages(self, start):
        if start < 0 or start > self._num_messages:
            raise InputError(description='Invalid Start index')
        if start + MSG_BLOCK >= self._num_messages:
            return list(self._messages[start:])
        return list(self._messages[start: start + MSG_BLOCK])

    def remove(self, message_id):
        if not self.message_exists(message_id):
            raise InputError(description='Message does not exist')

        self._messages.pop(message_id)
        self._num_messages -= 1

    def find(self, message_id):
        return self._messages[message_id]

    def search(self, query_string):
        return list(
            [msg for msg in self._messages if query_string in msg['message']])
    
    def next_id(self):
        return int(self._current_id + 1)


class UserMessage():
    '''
    Contains a structure that maintains the relationship
    between users, channels, reacts and messages they sent
    '''
    def __init__(self):
        self._user_messages = list()
        self._react_ids = [1]


    def add_link(self, u_id, channel_id, message_id):
        if self.link_exists(message_id):
            raise InputError(description='Message already exists')
        self._user_messages.append({
            'message_id': message_id,
            'u_id': u_id,
            'channel_id': channel_id,
            'reacts': []
        })

    def fetch_channel_msgs(self, start, ch_id):
        try:
            channel_msgs = list(filter(lambda x: x['channel_id'] == ch_id, self._user_messages))
        except:
            raise InputError(description="Channel does not exist")
        try:
            return list(channel_msgs[start:])
        except:
            raise InputError(description='Invalid start index')

    def remove_link_by_user(self, u_id):
        self._user_messages = list(filter(lambda x: x['u_id'] != u_id, self._user_messages))

    def remove_link_by_channel(self, channel_id):
        self._user_messages = list(
            filter(lambda x: x['channel_id'] != channel_id, self._user_messages))

    def remove_link_by_message(self, message_id):
        self._user_messages = list(filter(lambda x: x['message_id'] != message_id, self._user_messages))

    def link_exists(self, message_id):
        return message_id in [link['message_id'] for link in self._user_messages]

    def react(self, u_id, m_id, react_id):
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
        try:
            [info] = list(filter(lambda x: x['message_id'] == m_id, self._user_messages))
            return info
        except ValueError:
            return None

    def is_valid_react(self, react_id):
        return react_id in self._react_ids

    def is_sender(self, m_id, u_id):
        return u_id in [link['u_id'] for link in self._user_messages if link['message_id']] == m_id

    def channel_all_messages(self, ch_id):
        msg_dicts = list(filter(lambda msg: msg['channel_id'] == ch_id, self._user_messages))
        msg_ids = list(map(lambda msg: msg['message_id'], msg_dicts))
        return msg_ids

    def message_channel(self, message_id):
        for link in self._user_messages:
            # matching message_id -> return corresponding channel_id
            if message_id == link[0]:
                return int(link[2])

class UserChannel():
    '''
    Contains a structure that maintains the relationship
    between users and the channels they have joined
    '''
    def __init__(self):
        self._user_channels = list()

    def add_link(self, u_id, channel_id, is_owner):
        if self.link_exists(u_id, channel_id):
            raise InputError(description='user already in channel')

        self._user_channels.append((u_id, channel_id, is_owner))

    def remove_link_by_user(self, u_id):
        self._user_channels = list(filter(lambda x: x[0] == u_id, self._user_channels))

    def remove_link_by_channel(self, channel_id):
        self._user_channels = list(filter(lambda x: x[1] == channel_id, self._user_channels))

    def remove_user(self, u_id, channel_id):
        try:
            [to_remove] = list(
                filter(lambda x: x[0] == u_id and x[1] == channel_id, self._user_channels))
            self._user_channels.remove(to_remove)
        except ValueError:
            pass
    def add_owner(self, u_id, channel_id):
        if self.is_owner(u_id, channel_id):
            raise InputError(description='user is already an owner')
        #tuples cannot allow modification; therefore delete then add
        self.remove_user(u_id, channel_id)
        self.add_link(u_id, channel_id, is_owner=True)

    def remove_owner(self, u_id, channel_id):
        if not self.is_owner(u_id, channel_id):
            raise InputError(description='user is not an owner')

        #tuples are immutable; so we delete him then add him as a member
        self.remove_user(u_id, channel_id)
        self.add_link(u_id, channel_id, is_owner=False)

    def join_channel(self, u_id, channel_id):
        self.add_link(u_id, channel_id, is_owner=False)

    def leave_channel(self, u_id, channel_id):
        self.remove_user(u_id, channel_id)

    def link_exists(self, u_id, channel_id):
        return u_id in \
            [u_id for u_id, ch_id, _ in self._user_channels if ch_id == channel_id]

    def is_member(self, u_id, channel_id):
        return u_id in self.members(channel_id)

    def is_owner(self, u_id, channel_id):
        return u_id in self.owners(channel_id)

    def members(self, channel_id):
        return [u_id for u_id, ch_id, _ in self._user_channels if channel_id == ch_id]

    def owners(self, channel_id):
        return  [u_id for u_id, ch_id, is_owner in self._user_channels if \
                ch_id == channel_id and is_owner]

    def user_channels(self, given_u_id):
        return list([ch_id for u_id, ch_id, _ in self._user_channels if u_id == given_u_id])


class Database():
    def __init__(self):
        self.users = Users()
        self.admins = Admins()
        self.channels = Channels()
        self.messages = Messages()
        self.user_message = UserMessage()
        self.user_channel = UserChannel()

    def reset(self):
        self.__init__()

    def add_user(self, details):
        u_id = self.users.add(details)
        #first user is an admin
        if u_id == 1:
            self.admins.add(details)
        return u_id

    def add_channel(self, u_id, details):
        channel_id = self.channels.add(details)
        self.user_channel.add_link(u_id, channel_id, is_owner=True)
        return channel_id

    def channel_members(self, channel_id):
        member_ids = self.user_channel.members(channel_id)
        members_info = list(map(self.users.user_details, member_ids))
        return list([{
            'u_id': member['u_id'],
            'name_first':member['name_first'],
            'name_last': member['name_last']
        } for member in members_info])

    def channel_owners(self, channel_id):
        member_ids = self.user_channel.owners(channel_id)
        members_info = list(map(self.users.user_details, member_ids))
        return list([{
            'u_id': member['u_id'],
            'name_first':member['name_first'],
            'name_last': member['name_last']
        } for member in members_info])

    def channel_messages(self, u_id, details):
        channel_id, start = details
        #msgs_info = self.messages.fetch_messages(start)
        link_info = self.user_message.fetch_channel_msgs(start, channel_id)

        if start + MSG_BLOCK < len(link_info):
            link_info = link_info[start: start + MSG_BLOCK]
        msgs_info = list(
            map(lambda x: self.messages.message_details(x['message_id']), link_info))
        reacts_lists = [msg['reacts'] for msg in link_info]
        for reacts_list in reacts_lists:
            for react in reacts_list:
                react['is_this_user_reacted'] = True if u_id in react['u_ids'] else False

        full_info = list(map(lambda x, y: {
            'message_id': y['message_id'],
            'u_id': x['u_id'],
            'message': y['message'],
            'time_created': y['time_created'],
            'reacts': x['reacts'],
            'is_pinned': y['is_pinned']
        }, link_info, msgs_info))
        return list(full_info)

    def add_message(self, u_id, channel_id, details):
        message_id = self.messages.add(details)
        self.user_message.add_link(u_id, channel_id, message_id)
        return message_id

    def remove_message(self, message_id):
        self.messages.remove(message_id)
        self.user_message.remove_link_by_message(message_id)

    def user_channels(self, u_id):
        all_channels = self.channels.all()
        filtered_channels = self.user_channel.user_channels(u_id)
        return list([d for d in all_channels if d['channel_id'] in filtered_channels])

    def pin(self, u_id, message_id):
        #check message exists
        if not self.messages.message_exists(message_id):
            raise InputError(description='Message does not exist')

        #getting the channel_id in which the message was sent
        channel_id = self.user_message.message_channel(message_id)

        #validate the user is an owner or an admin of the channel
        if not self.user_channel.is_owner(u_id, channel_id) and not self.admins.is_admin(u_id):
            raise AccessError(description='You do not have access to pin message')

        self.messages.pin(message_id)

    def unpin(self, u_id, message_id):
        #checking message exists
        if not self.messages.message_exists(message_id):
            raise InputError(description='Message does not exist')

        #getting the channel_id in which the message was sent
        channel_id = self.user_message.message_channel(message_id)

        #user should be an owner or an admin
        if not self.user_channel.is_owner(u_id, channel_id) and not self.admins.is_admin(u_id):
            raise AccessError(description='You do not have access to pin message')

        self.messages.unpin(message_id)

STORE = Database()
# this dictionary contains the session tokens that
# won't need to be stored in the Store data dictionary for pickling
# {"token_str1": u_id1, "token_str2": u_id2, ..}
TOKENS = dict()


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
            STORE = {
                'users': {},
                'Slack_owners': [],
                'channels': {},
                'messages': [],
            }


def initialize_state():
    '''
    initialise the store and the tokens dictionary
    '''
    initialize_store()
    global TOKENS  # pylint: disable=global-statement
    TOKENS = dict()


# A constant to update the database every hour
SECONDS_TO_UPDATE = 1


class StateTimer(Timer):
    '''
    An simple abstraction over the timer class to
    run a function every n seconds
    '''

    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def update_database():
    '''
    pickle the state database into a file
    '''
    global STORE # pylint: disable=global-statement
    with open('database.p', "wb") as database_file:
        pickle.dump(STORE, database_file)

# a Timer to update the database every hour
DATABASE_UPDATER = StateTimer(SECONDS_TO_UPDATE, update_database)

def run_updater():
    '''
    a function that initializes the database updater in parallel
    '''
    DATABASE_UPDATER.run()
# the thread that parallelizes the work
UPDATE_THREAD = Thread(target=run_updater)

# initialize state when imported
initialize_state()
