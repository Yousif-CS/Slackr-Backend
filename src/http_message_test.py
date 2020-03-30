import pytest
import urls
import json
import urllib.request
from urllib.error import HTTPError

from http_helpers import reset, message_send

def test_message_send_ok():
    