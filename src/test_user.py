import pytest 
from error import InputError, AccessError
from user import user_profile, user_profile_setname, user_profile_setemail, user_profile_sethandle
from auth import auth_register, auth_login
from is_valid_email import is_valid_email


# creates users jwang and kli, and login
@pytest.fixture
def get_user_jwang():
    user_jwang = auth_register("joshua@gmail.com", "3.14159", "Joshua", "Wang")
    return (user_jwang["token"], user_jwang["u_id"])

@pytest.fixture
def get_user_kli():
    user_kli = auth_register("ken@gmail.com", "2.71828", "Ken", "Li")
    return (user_kli["token"], user_kli["u_id"])

'''------------------testing user_profile--------------------'''
# tests that 'user_profile' returns the information of the authorised user.
def test_access_own_profile(get_user_jwang):
    jwang_token, jwang_u_id = get_user_jwang
    assert user_profile(jwang_token, jwang_u_id) == \
        {"user": {
        	"u_id": jwang_u_id,
        	"email": "joshua@gmail.com",
        	"name_first": "Joshua",
        	"name_last": "Wang",
        	"handle_str": "joshuawang",
            }
        }

# test one user accessing the information of another valid user id
def test_access_other_profiles(get_user_jwang, get_user_kli):
    jwang_token, jwang_u_id = get_user_jwang
    kli_token, kli_u_id = get_user_kli

    # user kli accessing profile of user jwang
    assert user_profile(kli_token, jwang_u_id) == \
        {"user": {
        	"u_id": jwang_u_id,
        	"email": "joshua@gmail.com",
        	"name_first": "Joshua",
        	"name_last": "Wang",
        	"handle_str": "joshuawang",
            }
        }

    assert user_profile(jwang_token, kli_u_id) == \
        {"user": {
        	"u_id": kli_u_id,
        	"email": "ken@gmail.com",
        	"name_first": "Ken",
        	"name_last": "Li",
        	"handle_str": "kenli",
            }
        }

# test that an invalid u_id's will throw an InputError
def test_user_profile_invalid_string_id(get_user_kli):
    kli_token, kli_u_id = get_user_kli

    with pytest.raises(InputError):
        user_profile(kli_token, "abc")

def test_user_profile_invalid_float_id(get_user_kli):
    kli_token, kli_u_id = get_user_kli

    with pytest.raises(InputError):
        user_profile(kli_token, 2.75)

def test_user_profile_invalid_int_id(get_user_kli, get_user_jwang):
    kli_token, kli_u_id = get_user_kli
    jwang_token, jwang_u_id = get_user_jwang

    with pytest.raises(InputError):
        user_profile(jwang_token, (jwang_u_id) ** 2 + (kli_u_id) ** 2 + 1)

def test_user_profile_invalid_token(get_user_jwang, get_user_kli):
    jwang_token, jwang_u_id = get_user_jwang
    kli_token, kli_u_id = get_user_kli

    with pytest.raises(AccessError):
        user_profile(jwang_token + kli_token + "invalid", jwang_u_id)

    with pytest.raises(AccessError):
        user_profile(jwang_token + kli_token + "invalid", kli_u_id)

'''------------------testing user_profile_setname--------------------'''

# tests that authorised user can update their first and last name so long as input is valid
def test_user_profile_setname(get_user_kli, get_user_jwang):
    kli_token, kli_u_id = get_user_kli
    
    user_profile_setname(kli_token, "Kenneth", "Lithium")
    kli_profile = user_profile(kli_token, kli_u_id)["user"]

    assert kli_profile["name_first"] == "Kenneth"
    assert kli_profile["name_last"] == "Lithium"

# check that a name can contain upper and lower case letters in any combination
def test_setname_upperlower(get_user_jwang):
    jwang_token, jwang_u_id = get_user_jwang

    user_profile_setname(jwang_token, "jOnaThAn", "WeMbleYeYEYEY")
    jwang_profile = user_profile(jwang_token, jwang_u_id)["user"]

    assert jwang_profile["name_first"] == "jOnaThAn"
    assert jwang_profile["name_last"] == "WeMbleYeYEYEY"
    
# Check that white spaces are allowed in first- and last-names
def test_setname_whitespaces(get_user_jwang):
    jwang_token, jwang_u_id = get_user_jwang
    
    user_profile_setname(jwang_token, "Sue Anne", "Stein Holmes")
    jwang_profile = user_profile(jwang_token, jwang_u_id)["user"]

    assert jwang_profile["name_first"] == "Sue Anne"
    assert jwang_profile["name_last"] == "Stein Holmes"

# Check that symbols are allowed within names
def test_setname_symbols(get_user_kli):
    kli_token, kli_u_id = get_user_kli

    user_profile_setname(kli_token, "Sue-Anne", "Stein-Holmes")
    kli_profile = user_profile(kli_token, kli_u_id)["user"]

    assert kli_profile["name_first"] == "Sue-Anne"
    assert kli_profile["name_last"] == "Stein-Holmes"

# Check that names can be entirely symbols
def test_setname_allsymbols(get_user_kli):
    kli_token, kli_u_id = get_user_kli

    user_profile_setname(kli_token, "@#$%^&*(", ")(*&^%$#$%")
    kli_profile = user_profile(kli_token, kli_u_id)["user"]

    assert kli_profile["name_first"] == "@#$%^&*("
    assert kli_profile["name_last"] == ")(*&^%$#$%"

# Test that names can contain white spaces as long as they contain other characters
def test_setname_manywhitespaces(get_user_kli):
    kli_token, kli_u_id = get_user_kli

    user_profile_setname(kli_token, "   _D_   ", "    ?E-utschl@nd      ")
    kli_profile = user_profile(kli_token, kli_u_id)["user"]

    assert kli_profile["name_first"] == "   _D_   "
    assert kli_profile["name_last"] == "    ?E-utschl@nd      "

def test_setname_info_updates_for_other_users(get_user_kli, get_user_jwang):
    kli_token, kli_u_id = get_user_kli
    jwang_token, jwang_u_id = get_user_jwang

    user_profile_setname(kli_token, "   _D_   ", "    ?E-utschl@nd      ")
    kli_profile = user_profile(jwang_token, kli_u_id)["user"]

    assert kli_profile["name_first"] == "   _D_   "
    assert kli_profile["name_last"] == "    ?E-utschl@nd      "

# test that an input error is thrown for each of:
# 1. name_first empty
# 2. name_last empty
# 3. name_first over 50 char
# 4. name_last over 50 char
# names that are purely whitespaces are counted as invalid
def test_user_profile_setname_invalid_empty(get_user_kli):
    kli_token, kli_u_id = get_user_kli

    with pytest.raises(InputError):
        user_profile_setname(kli_token, "", "Lithium")
    with pytest.raises(InputError):
        user_profile_setname(kli_token, "Kenneth", "")

def test_user_profile_setname_invalid_toolong(get_user_kli):
    kli_token, kli_u_id = get_user_kli

    with pytest.raises(InputError):
        user_profile_setname(kli_token, "K" * 51, "Lithium")
    with pytest.raises(InputError):
        user_profile_setname(kli_token, "Kenneth", "L" * 51)

def test_user_profile_setname_invalid_whitespaces_only(get_user_kli):
    kli_token, kli_u_id = get_user_kli

    with pytest.raises(InputError):
        user_profile_setname(kli_token, "       ", "Li")
    with pytest.raises(InputError):
        user_profile_setname(kli_token, "Ken", "        ")

def test_user_profile_setname_invalid_token(get_user_jwang):
    jwang_token, jwang_u_id = get_user_jwang

    with pytest.raises(AccessError):
        user_profile_setname(jwang_token + "invalid", "Joshuat", "Wangt")

'''------------------testing user_profile_setemail--------------------'''

# test that authorised user can update their email address so long as it is valid
def test_user_profile_setemail(get_user_kli):
    kli_token, kli_u_id = get_user_kli
    
    user_profile_setemail(kli_token, "kenli@gmail.com")
    assert user_profile(kli_token, kli_u_id)["user"]["email"] == "kenli@gmail.com"

def test_user_profile_setemail_updates_for_other_users(get_user_kli, get_user_jwang):
    jwang_token, jwang_u_id = get_user_jwang
    kli_token, kli_u_id = get_user_kli

    user_profile_setemail(kli_token, "kenli@gmail.com")
    assert user_profile(jwang_token, kli_u_id)["user"]["email"] == "kenli@gmail.com"

def test_user_profile_setemail_contains_nums_symbols(get_user_jwang):
    jwang_token, jwang_u_id = get_user_jwang
    kli_token, kli_u_id = get_user_kli

    user_profile_setemail(jwang_token, "joshua_wang2@gmail.com")
    assert user_profile(jwang_token, jwang_uid)["user"]["email"] == "joshua_wang2@gmail.com"

    user_profile_setemail(jwang_token, "joshua.wang_2@gmail.com")
    assert user_profile(jwang_token, jwang_u_id)["user"]["email"] == "joshua.wa-ng_23@gmail.com"

def test_user_profile_setemail_unique_changes():
    pass

# test that invalid but unique emails throw input error
def test_invalid_email(get_user_kli, get_user_jwang):
    kli_token, kli_u_id = get_user_kli
    wang_token, jwang_u_id = get_user_jwang 
    pass
    #TODO: figure out all the ways an email could be invalid

# test that existing emails throw input error
def test_nonunique_email(get_user_kli, get_user_jwang):
    kli_token, kli_u_id = get_user_kli
    jwang_token, jwang_u_id = get_user_jwang
    pass

# test invalid token

'''------------------testing user_profile_sethandle--------------------'''

# test that authorised user can update their handle so long as it is valid and unique (3 char and 20 char)
def test_user_profile_sethandle(get_user_kli):
    kli_token, kli_u_id = get_user_kli

    user_profile_sethandle(kli_token, "")

# test that handles too short <3 throw InputError
# test that handles too long >20 throw InputError
# test that non-unique handles throw InputError
    pass
