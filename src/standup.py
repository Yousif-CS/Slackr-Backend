#pylint: disable=missing-module-docstring
from server import get_store, get_tokens

from auth import verify_token


#this is a dictionary of standups for each channel
#which contains the time it is created, the time it finishes,
#and the messages it has
standup_messages = {}

def getStandup():
    global standup_messages
    return standup_messages
    
def standup_active():
    pass