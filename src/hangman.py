'''
This file contains the functions necessary for the implementation of the hangman game,
which should be able to run within each channel of the slackr
'''
import random
import string
from state import get_store

word_file = "/usr/share/dict/words"
with open(word_file) as FILE:   
    WORDS = FILE.read().splitlines()

MAX_LIVES = 7
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

def start_game(channel_id):
    '''
    Input: channel_id
    Output: temporary database in which to store the word to guess,
    and the letters of the alphabet as well as whether each letter has been guessed.
    Unique to each channel; assuming only one game per channel at a time.
    Turns on hangman mode in state.py
    '''
    data = get_store().channels.get_hangman(channel_id)
    target_word = generate_word()
    data = {
        "target_word": target_word,
        "user_guess": ['?' for letter in target_word],
        # dictionary with alphabet letters as keys and values default to False
        "letters_guessed": dict.fromkeys(string.ascii_uppercase, False), 
        "lives_remaining": MAX_LIVES,
        "game_end": False,
        "output": ""
    }

    data['output'] += "Let's play Hangman!"
    data['output'] += "\nType /guess X to guess letter X."
    data['output'] += "\nType /quit to end the game."
    data['output'] += f"\nYou have {data['lives_remaining']} lives remaining."
    data['output'] += "\nThe word to guess is:"
    data['output'] += '\n' + ' '.join(data['user_guess'])

    return data

def guess(letter, channel_id, name_first):
    '''
    Inputs: letter guessed by the user, channel_id, first name of user
    Output: hangman data dictionary with updates to user_guess, letters_guessed, lives_remaining, game_end and output
    based on the user's guess.

    When the user guesses whether a letter is in the word,
    inform the user that:
    a. the guess is correct
    b. the guess is incorrect
    c. the guess is invalid (not alpha or not single char)
    '''
    data = get_store().channels.get_hangman(channel_id)

    # letter already guessed
    if data['letters_guessed'][letter.upper()] is True:
        guessed = ', '.join([ltr for ltr in list(data['letters_guessed'].keys()) if data['letters_guessed'][ltr]])
        data['output'] = f"Letters guessed so far are: {guessed}."
        data['output'] += "\nThis letter has already been guessed, please enter another letter."
        data['output'] += '\n\n' + ' '.join(data['user_guess'])

    # correct guess
    elif letter.upper() in data['target_word']:
        data['letters_guessed'][letter.upper()] = True

        # udpate the user_guess to reveal all letters correctly guessed so far
        i = 0
        while i < len(data['target_word']):
            if data['target_word'][i] == letter.upper():
                data['user_guess'][i] = letter.upper()
            i += 1

        data['output'] = "That's right! "
        
        if '?' not in data['user_guess']:
            # user wins the game with this guess
            data['game_end'] = True
            data['output'] += 'The word was ' + ''.join(data['user_guess'])
            data['output'] += f"\nCongratulations {name_first}! You win! \
                \nType /hangman to start a new game."
        else:
            guessed = ', '.join([ltr for ltr in list(data['letters_guessed'].keys()) if data['letters_guessed'][ltr]])
            data['output'] += f"\nLetters guessed so far are: {guessed}."
            data['output'] += '\n\n' + ' '.join(data['user_guess'])

    # incorrect guess
    else:
        data['letters_guessed'][letter.upper()] = True
        data['lives_remaining'] -= 1
        
        if data['lives_remaining'] == 0:
            # User runs out of lives, loses, game ends.
            data['game_end'] = True
            data['output'] = f"\nYou lose! It was all {name_first}'s fault :("
            data['output'] += "\nDidn't you know the word was " + ''.join(data['target_word']) + "?"
            data['output'] += "\nType /hangman to restart."
        else:
            data['output'] = f"That's wrong, you have {data['lives_remaining']} lives remaining."
            guessed = ', '.join([ltr for ltr in list(data['letters_guessed'].keys()) if data['letters_guessed'][ltr]])
            data['output'] += f"\nLetters guessed so far are: {guessed}."
            data['output'] += '\n\n' + ' '.join(data['user_guess'])

    return data
