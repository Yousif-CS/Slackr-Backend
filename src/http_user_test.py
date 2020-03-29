'''
HTTP tests for user.py functions
'''
import pytest
import urls
import json
import urllib.request
from error import RequestError
from urllib.error import HTTPError
from http_helpers import reset, register, login, logout, user_profile, user_profile_setname, user_profile_setemail, \
    user_profile_sethandle
from time import sleep


def test_user_profile_own(reset):
    j_id, j_token = register("joshwang@gmail.com", "cre4t1v3p4s5", "Joshua", "Wang")
    payload = user_profile(j_token, j_id)
    assert payload == {
        "u_id": j_id,
        "email": "joshwang@gmail.com",
        "name_first": "Joshua",
        "name_last": "Wang",
        "handle_str": "joshuawang"
    }
    logout(j_token)

def test_user_profile_does_not_exist():
    j_id, j_token = login("joshwang@gmail.com", "cre4t1v3p4s5")
    with pytest.raises(HTTPError):
        user_profile(j_token, j_id+1)
    logout(j_token)

def test_user_profile():
    j_id, j_token = login("joshwang@gmail.com", "cre4t1v3p4s5")
    k_id, k_token = register("kenligordon@gmail.com", "IAMAMUSICIAN", "Ken", "Li")

    payload = user_profile(j_token, k_id)
    assert payload == {
        "u_id": k_id,
        "email": "kenligordon@gmail.com",
        "name_first": "Ken",
        "name_last": "Li",
        "handle_str": "kenli"
    }

    logout(j_token)
    logout(k_token)

def test_user_profile_data_missing():
    j_id, j_token = login("joshwang@gmail.com", "cre4t1v3p4s5")

    data = json.dumps({
        "token": j_token
    }).encode()

    request = urllib.request.Request(urls.PROFILE_URL, data=data, \
        method='GET', headers={'Content-Type':'application/json'})

    with pytest.raises(urllib.error.HTTPError):
        urllib.request.urlopen(request)

# can set name
def test_user_profile_setname():
    '''
    HTTP wrapper for changing the name of the authorised user
    '''
    j_id, j_token = login("joshwang@gmail.com", "cre4t1v3p4s5")
    
    user_profile_setname(j_token, "Freddie", "Mercury")
    profile = user_profile(j_token, j_id)

    assert profile["name_first"] == "Freddie"
    assert profile["name_last"] == "Mercury"

    logout(j_token)

# reject empty names and too long names

# can set email
def test_user_profile_setemail(reset):
    j_id, j_token = register("joshwang@gmail.com", "cre4t1v3p4s5", "Joshua", "Wang")

    user_profile_setemail(j_token, "yoshidino6263@gmail.com")
    profile = user_profile(j_token, j_id)

    assert profile["email"] == "yoshidino6263@gmail.com"

# reject if not unique
# reject if not valid email

# can set handle
def test_user_profile_sethandle(reset):
    j_id, j_token = register("joshwang@gmail.com", "cre4t1v3p4s5", "Joshua", "Wang")

    user_profile_sethandle(j_token, "fredmerc1")
    profile = user_profile(j_token, j_id)

    assert profile["handle_str"] == "fredmerc1"

# reject if not between 2 and 20 char
# reject if not unique
