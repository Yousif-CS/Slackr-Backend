import json
import urllib.request
from urllib.error import HTTPError
import pytest

import urls
from http_helpers import reset, register, login, channels_list

def test_channels_list_empty(reset):
    a_id, a_token = register('admin@gmail.com', 'pass123456', 'Alan', 'Brown')
    payload = channels_list(a_token)
    assert payload == []
