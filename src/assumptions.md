# Assumptions
##### This file contains assumptions made while testing backend functions
===================================================================================================
##### The structure of this file involves functions as headers and the assumptions as bullet points
---------------------------------------------------------------------------------------------------
# Overarching assumptions
1. The handle is a lower case concatenation of the first-name initial and the last-name. If this handle is already taken, an integer is concatenated to the end, ascending from 1.
2. Assume that names that are purely whitespaces are not valid.

### Channel functions:

#### channels_messages():
1. Assuming that the email addresses provided exists for registration
2. Assuming that 'owner' in this context refers only to a channel owner but not workspace owner as a global permission 
3. Assuming big ints such as 123123 are considered invalid channel id
4. Assuming 'I am an invalid token' string to be an invalid token
5. Assuming the function throws an 'AccessError' exception when dealing with invalid tokens

#### channel_leave():
3. Assuming big ints such as 123123 are considered invalid channel id's (at least initially)
4. Assuming 'I am an invalid token' string to be an invalid token
5. Assuming the function throws an 'AccessError' exception when dealing with invalid tokens

#### channel_join():
1. Assuming big ints such as 1232123 are considered invalid channel id's
2. Assuming that double joining raises some kind of exception
#### channel_addowner():

#### channel_removeowner():

### User functions
1. Assuming that auth_login functions as per the spec.


#### user_profile(token, u_id):
1. Assume that the returned value will be a dictionary of the following form:
    ```python
	{'user': {
        	'u_id': 1,
        	'email': 'cs1531@cse.unsw.edu.au',
        	'name_first': 'Hayden',
        	'name_last': 'Jacobs',
        	'handle_str': 'hjacobs',
        }
    }
	```
2. Assume that a correct token will always be provided

#### user_profile_setname(token, name_first, name_last):
1. Assume that the 'user_profile' function behaves correctly
2. Assume that 'name_*' containing white spaces only is invalid

#### user_profile_setemail(token, email):
1. Assume that the email provided exists.

#### user_profile_sethandle(token, handle_str):

#### users_all(token)