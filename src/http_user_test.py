'''
HTTP tests for user.py functions
'''
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=unused-import
import json
import urllib.request
from urllib.error import HTTPError
import pytest
import urls
from http_helpers import (reset, register, login, logout,
                          user_profile, user_profile_setname,
                          user_profile_setemail, user_profile_sethandle)


def test_user_profile_own(reset):
    '''
    getting your own information
    '''
    j_id, j_token = register("joshwang@gmail.com",
                             "cre4t1v3p4s5", "Joshua", "Wang")
    payload = user_profile(j_token, j_id)
    assert payload == {
        "u_id": j_id,
        "email": "joshwang@gmail.com",
        "name_first": "Joshua",
        "name_last": "Wang",
        "handle_str": "joshuawang",
        "profile_img_url": ""
    }
    logout(j_token)


def test_user_profile_does_not_exist():
    '''
    user does not exist
    '''
    j_id, j_token = login("joshwang@gmail.com", "cre4t1v3p4s5")
    with pytest.raises(HTTPError):
        user_profile(j_token, j_id + 1)
    logout(j_token)


def test_user_profile():
    '''
    valid request
    '''
    j_token = login("joshwang@gmail.com", "cre4t1v3p4s5")[1]
    k_id, k_token = register("kenligordon@gmail.com",
                             "IAMAMUSICIAN", "Ken", "Li")

    payload = user_profile(j_token, k_id)
    assert payload == {
        "u_id": k_id,
        "email": "kenligordon@gmail.com",
        "name_first": "Ken",
        "name_last": "Li",
        "handle_str": "kenli",
        "profile_img_url": ""
    }

    logout(j_token)
    logout(k_token)


def test_user_profile_logged_out():
    '''
    info of a logged out user
    '''
    j_token = login("joshwang@gmail.com", "cre4t1v3p4s5")[1]
    k_id, k_token = login("kenligordon@gmail.com", "IAMAMUSICIAN")

    logout(k_token)

    payload = user_profile(j_token, k_id)
    assert payload == {
        "u_id": k_id,
        "email": "kenligordon@gmail.com",
        "name_first": "Ken",
        "name_last": "Li",
        "handle_str": "kenli",
        "profile_img_url": ""
    }

    logout(j_token)


def test_user_profile_data_missing():
    '''
    missing first and last
    '''
    j_token = login("joshwang@gmail.com", "cre4t1v3p4s5")[1]

    data = json.dumps({
        "token": j_token
    }).encode()

    request = urllib.request.Request(urls.PROFILE_URL, data=data,
                                     method='GET', headers={'Content-Type': 'application/json'})

    with pytest.raises(HTTPError):
        urllib.request.urlopen(request)

# can set name


def test_user_profile_setname(reset):
    '''
    valid request to set name
    '''
    j_id, j_token = register("joshwang@gmail.com",
                             "cre4t1v3p4s5", "Joshua", "Wang")

    user_profile_setname(j_token, "Freddie", "Mercury")
    profile = user_profile(j_token, j_id)

    assert profile["name_first"] == "Freddie"
    assert profile["name_last"] == "Mercury"

# reject empty names and too long names


def test_user_profile_setname_empty_first(reset):
    '''
    First name empty
    '''
    j_token = register("joshwang@gmail.com",
                       "cre4t1v3p4s5", "Joshua", "Wang")[1]
    with pytest.raises(HTTPError):
        user_profile_setname(j_token, "", "Mercury")


def test_user_profile_setname_empty_last(reset):
    '''
    last name empty
    '''
    j_token = register("joshwang@gmail.com",
                       "cre4t1v3p4s5", "Joshua", "Wang")[1]
    with pytest.raises(HTTPError):
        user_profile_setname(j_token, "Freddie", "")


def test_user_profile_setname_first_over_50(reset):
    '''
    long name
    '''
    j_token = register("joshwang@gmail.com",
                       "cre4t1v3p4s5", "Joshua", "Wang")[1]
    with pytest.raises(HTTPError):
        user_profile_setname(j_token, "A" * 51, "Mercury")


def test_user_profile_setname_last_over_50(reset):
    '''
    long name
    '''
    j_token = register("joshwang@gmail.com",
                       "cre4t1v3p4s5", "Joshua", "Wang")[1]
    with pytest.raises(HTTPError):
        user_profile_setname(j_token, "Freddie", "M" * 51)

# data missing


def test_user_profile_setname_data_missing(reset):
    '''
    missing token
    '''
    data = json.dumps({
        "name_first": "data",
        "name_last": "missing"
    }).encode()
    request = urllib.request.Request(urls.SETNAME_URL, data=data,
                                     method='PUT', headers={"Content-Type": "application/json"})

    with pytest.raises(HTTPError):
        urllib.request.urlopen(request)


def test_user_profile_setname_data_missing_2(reset):
    '''
    missing first name
    '''
    j_token = register("joshwang@gmail.com",
                       "cre4t1v3p4s5", "Joshua", "Wang")[1]
    data = json.dumps({
        "token": j_token,
        "name_last": "data-missing"
    }).encode()
    request = urllib.request.Request(urls.SETNAME_URL, data=data,
                                     method='PUT', headers={"Content-Type": "application/json"})

    with pytest.raises(HTTPError):
        urllib.request.urlopen(request)


def test_user_profile_setemail(reset):
    '''
    can set email
    '''
    j_id, j_token = register("joshwang@gmail.com",
                             "cre4t1v3p4s5", "Joshua", "Wang")

    user_profile_setemail(j_token, "yoshidino6263@gmail.com")
    profile = user_profile(j_token, j_id)

    assert profile["email"] == "yoshidino6263@gmail.com"


def test_user_profile_setemail_reject_invalid(reset):
    '''
    reject if not valid email
    '''
    j_token = register("joshwang@gmail.com",
                       "cre4t1v3p4s5", "Joshua", "Wang")[1]
    with pytest.raises(HTTPError):
        user_profile_setemail(j_token, "joshwang@g-mail.co m")

# data missing


def test_user_profile_setemail_data_missing(reset):
    '''
    missing names
    '''
    j_token = register("joshwang@gmail.com",
                       "cre4t1v3p4s5", "Joshua", "Wang")[1]
    data = json.dumps({
        'token': j_token
    }).encode()
    request = urllib.request.Request(urls.SETEMAIL_URL, data=data,
                                     method='PUT', headers={'Content-Type': 'application/json'})

    with pytest.raises(HTTPError):
        urllib.request.urlopen(request)

# can set handle


def test_user_profile_sethandle(reset):
    '''
    Valid request to set handle
    '''
    j_id, j_token = register("joshwang@gmail.com",
                             "cre4t1v3p4s5", "Joshua", "Wang")

    user_profile_sethandle(j_token, "fredmerc1")
    profile = user_profile(j_token, j_id)

    assert profile["handle_str"] == "fredmerc1"

# reject if not between 2 and 20 char


def test_user_profile_sethandle_too_short(reset):
    '''
    very short handle
    '''
    j_token = register("joshwang@gmail.com",
                       "cre4t1v3p4s5", "Joshua", "Wang")[1]

    with pytest.raises(HTTPError):
        user_profile_sethandle(j_token, "j")


def test_user_profile_sethandle_too_long(reset):
    '''
    very long handle
    '''
    j_token = register("joshwang@gmail.com",
                       "cre4t1v3p4s5", "Joshua", "Wang")[1]

    with pytest.raises(HTTPError):
        user_profile_sethandle(j_token, "j" * 21)

# reject if not unique


def test_user_profile_setemail_reject_nonunique(reset):
    '''
    handle is used by someone else
    '''
    j_token = register("joshwang@gmail.com",
                       "cre4t1v3p4s5", "Joshua", "Wang")[1]
    register("kenligordon@gmail.com", "IAMAMUSICIAN", "Ken", "Li")

    with pytest.raises(HTTPError):
        user_profile_sethandle(j_token, "kenli")

# data missing


def test_user_profile_sethandle_data_missing(reset):
    '''
    missing handle
    '''
    j_token = register("joshwang@gmail.com",
                       "cre4t1v3p4s5", "Joshua", "Wang")[1]

    data = json.dumps({
        'token': j_token
    }).encode()

    request = urllib.request.Request(urls.SETHANDLE_URL, data=data,
                                     method='PUT', headers={'Content-Type': 'application/json'})

    with pytest.raises(HTTPError):
        urllib.request.urlopen(request)

# tests for invalid token


def test_user_profile_invalid_token(reset):
    '''
    invalid request with invalid token
    '''
    j_id, j_token = register("joshwang@gmail.com",
                             "cre4t1v3p4s5", "Joshua", "Wang")
    with pytest.raises(HTTPError):
        user_profile(j_token + 'x', j_id)


def test_user_profile_setname_invalid_token(reset):
    '''
    invalid request with invalid token
    '''
    j_token = register("joshwang@gmail.com",
                       "cre4t1v3p4s5", "Joshua", "Wang")[1]
    with pytest.raises(HTTPError):
        user_profile_setname(j_token + 'x', "Freddie", "Mercury")


def test_user_profile_setemail_invalid_token(reset):
    '''
    invalid request with invalid token
    '''
    j_token = register("joshwang@gmail.com",
                       "cre4t1v3p4s5", "Joshua", "Wang")[1]
    with pytest.raises(HTTPError):
        user_profile_setemail(j_token + 'x', "yoshidino266@gmia.com")


def test_user_profile_sethandle_invalid_token(reset):
    '''
    invalid request with invalid token
    '''
    j_token = register("joshwang@gmail.com",
                       "cre4t1v3p4s5", "Joshua", "Wang")[1]
    with pytest.raises(HTTPError):
        user_profile_sethandle(j_token + 'x', "joshwang234")
