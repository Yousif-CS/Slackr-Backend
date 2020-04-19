'''
This file contains the functions necessary for the implementation of the hangman game,
which should be able to run within each channel of the slackr.

A 'hangman bot' is registered for each new channel and cannot be removed from the slackr.
It informs users of the games progress through pre-programmed responses.

Admins and owners of each channel are able to enable and disable the game.
'''

# pylint: disable=trailing-whitespace
# pylint: disable=too-many-branches

import random
import string
import hashlib
from state import get_store, get_tokens
from error import InputError, AccessError
from auth import generate_token, create_handle

# file from which words are drawn
WORD_FILE = "/usr/share/dict/words"
with open(WORD_FILE) as FILE:
    WORDS = FILE.read().splitlines()

MAX_LIVES = 9
MAX_WORD_LEN = 10


def generate_word():
    '''
    Generates a random word from /usr/share/dict/words
    that is 10 letters long or less, and returns it.
    '''
    word = random.choice(WORDS)
    while len(word) > MAX_WORD_LEN:
        word = random.choice(WORDS)

    return list(word.upper())


def create_hbot(ch_id):
    '''
    Helper function called in channels_create to create a hangman bot with a unique email
    based on the ID of the channel it belongs to.

    Returns:
        Dictionary: containing the u_id and token of the bot.
    '''
    data = get_store()

    email = f'hangman{ch_id}@bot.com'
    password = 'botbotbot'
    name_first = 'Hangman'
    name_last = 'B0T'

    # hash the password
    encrypted_pass = hashlib.sha256(password.encode()).hexdigest()

    # Adds all user's details to the Database
    details = email, encrypted_pass, name_first, name_last, create_handle(
        name_first, name_last)
    hbot_id = data.add_user(details)
    hbot_token = generate_token(hbot_id)
    get_tokens()[hbot_token] = hbot_id

    # Add the Hangman Bot to the channel just created
    data.user_channel.add_link(hbot_id, ch_id, is_owner=True)
    data.channels.add_hbot_details(ch_id, hbot_id, hbot_token)

    return {
        'id': hbot_id,
        'token': hbot_token
    }


def start_game(channel_id):
    '''
    Lets the channel know that a hangman game is in session and returns all the data
    necessary to facilitate a game.

    Args:
        channel_id (str)

    Return:
        data (dictionary):
            target_word (str): the word the users are attempting to guess
            user_guess (list): the letters the users have guessed so far, '?' if not yet guessed
            ltrs_guessed (dictionary): all the upper case letters with Boolean values of whether
                they have been guessed.
            lives (int): lives remaining
            game_end (bool): whether the game has ended
            output (str): information to be sent to the user as a message

    '''
    data = get_store().channels.get_hangman(channel_id)
    target_word = generate_word()
    data = {
        "target_word": target_word,
        "user_guess": ['?' for letter in target_word],
        # dictionary with alphabet letters as keys and values default to False
        "ltrs_guessed": dict.fromkeys(string.ascii_uppercase, False),
        "lives": MAX_LIVES,
        "game_end": False,
        "output": ""
    }

    data['output'] += "Let's play Hangman!"
    data['output'] += "\nType /guess X to guess letter X."
    data['output'] += "\nType /quit to end the game."
    data['output'] += f"\nYou have {data['lives']} lives remaining."
    data['output'] += "\nThe word to guess is:"
    data['output'] += '\n' + ' '.join(data['user_guess'])

    return data


def guess(letter, channel_id, name_first):
    '''
    Updates the backend data as well as what the next message sent to the user should be
    based on the user's guess.
    Ends the game if either the users win by guessing the correct word, or
    the users lose by running out of lives.

    Args:
        letter (str): user's guess
        channel_id (int): current channel's ID
        name_first (str): first name of the user making the guess

    Returns:
        data (dictionary):
            target_word (str): the word the users are attempting to guess
            user_guess (list): the letters the users have guessed so far, '?' if not yet guessed
            ltrs_guessed (dictionary): all the upper case letters with Boolean values of whether
                they have been guessed.
            lives (int): lives remaining
            game_end (bool): whether the game has ended
            output (str): information to be sent to the user as a message

    '''
    data = get_store().channels.get_hangman(channel_id)

    # letter already guessed
    if data['ltrs_guessed'][letter.upper()] is True:
        guessed = ', '.join(
            [ltr for ltr in data['ltrs_guessed'] if data['ltrs_guessed'][ltr]])
        data['output'] = f"Letters guessed so far are: {guessed}."
        data['output'] += f"\nThe letter {letter.upper()} has already been guessed,\
             please enter another letter."
        data['output'] += '\n\n' + ' '.join(data['user_guess'])

    # correct guess
    elif letter.upper() in data['target_word']:
        data['ltrs_guessed'][letter.upper()] = True

        # udpate the user_guess to reveal all letters correctly guessed so far
        i = 0
        while i < len(data['target_word']):
            if data['target_word'][i] == letter.upper():
                data['user_guess'][i] = letter.upper()
            i += 1

        data['output'] = "That's right! "

        # user wins the game with this guess and ends the game
        if '?' not in data['user_guess']:
            data['game_end'] = True
            data['output'] += 'The word was ' + ''.join(data['user_guess'])
            data['output'] += f"\nCongratulations {name_first}! You win! \
                \nType /hangman to start a new game."
        else:
            guessed = ', '.join(
                [ltr for ltr in data['ltrs_guessed'] if data['ltrs_guessed'][ltr]])
            data['output'] += f"\nLetters guessed so far are: {guessed}."
            data['output'] += '\n\n' + ' '.join(data['user_guess'])

    # incorrect guess
    else:
        data['ltrs_guessed'][letter.upper()] = True
        data['lives'] -= 1

        # User runs out of lives, ending game.
        if data['lives'] == 0:
            data['game_end'] = True
            data['output'] = f"\nYou lose! It was all {name_first}'s fault :("
            data['output'] += "\nDidn't you know the word was " + \
                ''.join(data['target_word']) + "?"
            data['output'] += "\nType /hangman to restart."
        else:
            if data['lives'] > 1:
                data['output'] = f"That's wrong, you have {data['lives']} lives remaining."
            else:
                data['output'] = f"That's wrong, you have 1 life remaining."
            guessed = ', '.join([ltr for ltr in list(data['ltrs_guessed'].keys(
            )) if data['ltrs_guessed'][ltr]])  # pylint: disable=line-too-long
            data['output'] += f"\nLetters guessed so far are: {guessed}."
            data['output'] += '\n\n' + ' '.join(data['user_guess'])

    return data


def hangman(message, channel_id, u_id):
    '''
    Helper function in message_send to detect the commands
    '/hangman', '/guess', '/quit', '/enable game', '/disable game'.

    Args:
        message (str): obtained from message_send to scan for commands
        channel_id (int): of the current channel
        u_id (int): of the user sending the message
    '''
    data = get_store()

    # variable to keep track of message to send back to user
    hbot_output = None

    if message == '/hangman' and data.channels.is_hangman_enabled(channel_id):
        # idempotency of /hangman command
        if data.channels.is_hangman_running(channel_id):
            raise InputError(description="Hangman is already running")
        # obtain all the base data needed to start a game of hangman
        hangman_data = start_game(channel_id)
        # store this data as part of the channel's info
        data.channels.start_hangman(channel_id, hangman_data)
        # obtain the message for the bot to send back
        hbot_output = data.channels.get_hangman(channel_id)['output']

    elif data.channels.is_hangman_running(channel_id):
        if message.startswith('/guess'):
            try:
                letter = message.split(" ", 1)[1].strip()
                # update the hangman dictionary based on the user's guess
                new_details = guess(
                    letter, channel_id, data.users.user_details(u_id)['name_first'])
                data.channels.edit_hangman(channel_id, new_details)
                hbot_output = new_details['output']

                if new_details['game_end'] is True:
                    data.channels.quit_hangman(channel_id)
            except BaseException:
                raise InputError(
                    description="Please enter a single letter to guess!")

        elif message == '/quit':
            data.channels.quit_hangman(channel_id)
            hbot_output = "Quitting game. Goodbye!"

        elif message == '/disable game':
            # command should only work for admins and channel owners
            if data.admins.is_admin(
                    u_id) or data.user_channel.is_owner(u_id, channel_id):
                data.channels.quit_hangman(channel_id)
                hbot_output = "Quitting game. Goodbye! \
                    \nHangman disabled. Type '/enable game' to re-enable the game."
            else:
                raise AccessError(
                    description="You do not have permission to change game settings in this channel")  # pylint: disable=line-too-long
    else:
        if message == '/disable game':
            # command should only work for admins and channel owners
            if data.admins.is_admin(
                    u_id) or data.user_channel.is_owner(u_id, channel_id):
                data.channels.disable_hangman(channel_id)
                hbot_output = "Hangman disabled. \nType '/enable game' to re-enable the game."
            else:
                raise AccessError(
                    description="You do not have permission to change game settings in this channel")  # pylint: disable=line-too-long
        elif message == '/enable game':
            # command should only work for admins and channel owners
            if data.admins.is_admin(
                    u_id) or data.user_channel.is_owner(u_id, channel_id):
                data.channels.enable_hangman(channel_id)
                hbot_output = "Hangman enabled. \nType '/disable game' to disable the game."
            else:
                raise AccessError(
                    description="You do not have permission to change game settings in this channel")  # pylint: disable=line-too-long

    return hbot_output
