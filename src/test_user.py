import pytest 
from error import InputError
from user import user_profile, user_profile_setname, user_profile_setemail, user_profile_sethandle
from auth import auth_register, auth_login


# create users jwang and kli, and loging
@pytest.fixture
def get_user_jwang():
    user_jwang = auth_register("joshua@gmail.com", "3.14159", "Joshua", "Wang")
    return (user_jwang["u_id"], user_jwang["token"])

@pytest.fixture
def get_user_kli():
    user_kli = auth_register("ken@gmail.com", "2.71828", "Ken", "Li")
    return (user_kli["u_id"], kli_token)

'''------------------testing user_profile--------------------'''
# tests that 'user_profile' returns the information of the authorised user.
def test_access_own_profile(get_user_jwang, get_user_kli):
    jwang_token, jwang_u_id = get_user_jwang
    assert user_profile(jwang_token, jwang_u_id) == \
        {"user": {
        	"u_id": jwang_u_id,
        	"email": "joshua@gmail.com",
        	"name_first": "Joshua",
        	"name_last": "Wang",
        	"handle_str": "jwang",
            }
        }
    
    kli_token, kli_u_id = get_user_kli
    assert user_profile(kli_token, kli_u_id) == \
        {"user": {
        	"u_id": kli_u_id,
        	"email": "ken@gmail.com",
        	"name_first": "Ken",
        	"name_last": "Li",
        	"handle_str": "kli",
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
        	"handle_str": "jwang",
            }
        }

# test that an invalid u_id (string) will throw an InputError
def test_user_profile_invalid_u_id(get_user_kli):
    kli_token, kli_u_id = get_user_kli

    with pytest.raises(InputError):
        user_profile(kli_token, "abc")

'''------------------testing user_profile_setname--------------------'''

# tests that authorised user can update their first and last name so long as input is valid
def test_user_profile_setname(get_user_kli):
    kli_token, kli_u_id = get_user_kli

    user_profile_setname(kli_token, "Kenneth", "Lithium")
    assert user_profile(kli_token, kli_u_id) == \
        {"user": {
        	"u_id": kli_u_id,
        	"email": "ken@gmail.com",
        	"name_first": "Kenneth",
        	"name_last": "Lithium",
        	"handle_str": "kli",
            }
        }

# test that an input error is thrown for each of:
# 1. name_first empty
# 2. name_last empty
# 3. name_first over 50 char
# 4. name_last over 50 char
# 5. names that are purely whitespaces are counted as invalid
def test_user_profile_setname_invalid(get_user_kli):
    kli_token, kli_u_id = get_user_kli

    with pytest.raises(InputError):
        user_profile_setname(kli_token, "", "Lithium")
        user_profile_setname(kli_token, "Kenneth", "")
        user_profile_setname(kli_token, "K" * 51, "Lithium")
        user_profile_setname(kli_token, "Kenneth", "L" * 51)
        user_profile_setname(kli_token, "       ", "Li")
        user_profile_setname(kli_token, "Ken", "        ")

# test that authorised user can update their email address so long as it is valid and unique
def test_user_profile_setemail():
    

# test that invalid emails throw input error
# test that existing emails throw input error

# test that authorised user can update their handle so long as it is valid and unique (3 char and 20 char)
def test_user_profile_sethandle():
# test that handles too short <3 throw InputError
# test that handles too long >20 throw InputError
# test that non-unique handles throw InputError

def test_users_all():
    # tests that it returns a dictionary containing a dictionary of all the users