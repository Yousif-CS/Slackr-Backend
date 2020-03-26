'''
Using requests module to test channel functions
'''

import requests
import json 
import pytest
import urls


#Testing channel_messages
def test_channel_messages_empty(reset, register):
    my_u_id, my_token = register
