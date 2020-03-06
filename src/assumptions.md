# This file contains assumptions made while testing backend functions
===================================================================================================
## The structure of this file involves functions as headers and the assumptions as bullet points
---------------------------------------------------------------------------------------------------
# Overarching assumptions
1. The handle is a lower case concatenation of the first-name initial and the last-name. If this handle is already taken, an integer is concatenated to the end, ascending from 1.
2. Assume that names that are purely whitespaces are not valid.

### Channel functions:
The main assumption is that we only need to register the user once, and afterwards, we can log them in each time we test a certain function, that is, we assume that there is a database storing login details 

#### channels_messages():
1. Assuming that the email addresses provided exists for registration
2. Assuming that the channel is empty once it is created (contains no messages)
3. Assuming that 'owner' in this context refers only to a channel owner but not workspace owner as a global permission 
4. Assuming big ints such as 123123 are considered invalid channel id
5. Assuming 'I am an invalid token' string to be an invalid token
6. Assuming the function throws an 'AccessError' exception when dealing with invalid tokens

#### channel_leave():
1. Assuming big ints such as 123123 are considered invalid channel id's (at least initially)
2. Assuming 'I am an invalid token' string to be an invalid token
3. Assuming the function throws at least a general 'Exception' when dealing with invalid tokens

#### channel_join():
1. Assuming big ints such as 1232123 are considered invalid channel id's
2. Assuming that double joining raises some kind of exception

#### channel_addowner():
1. Assuming an int like 22222 is considered an invalid channel id
2. Assuming 'I am an invalid token' string to be an invalid token
3. Assuming the function throws at least a general 'Exception' when dealing with invalid tokens

#### channel_removeowner():
1. Assuming an int like 22222 is considered an invalid channel id

### Channels functions():

#### channels_list():
1. Assuming that newly registered users are not part of any channel

#### channels_listall():
1. Assuming that both public and private channels are visible when this function is called 

#### channels_create():
1. Assuming channel_id begins indexing from 1
2. Assuming that empty strings are allowed for channel names, which may have some 'NoName' placeholder in frontend

### Message functions 
#### message_send():
1. Assuming that messages that are empty strings or white spaces are allowed
2. Assuming that an invalid channel_id will also throw some error



### User functions
1. Assuming that auth_login works as per the spec.

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
2. Assume that a correct token will always be provided.

#### user_profile_setname(token, name_first, name_last):
1. Assume that the 'user_profile' function behaves correctly.
2. Assume that 'name_*' containing white spaces only is invalid.
3. First- and last-names can be more than one word each. E.g. Sue Anne is a valid name_first.
4. Names can contain and consist only of symbols.
5. Assume that names can contain whitespaces as long as they also contain other characters.

#### user_profile_setemail(token, email):
1. Assume that the email provided exists.

#### user_profile_sethandle(token, handle_str):

#### users_all(token)