# This file contains assumptions made while testing backend functions
===================================================================================================
## The structure of this file involves functions as headers and the assumptions as bullet points
---------------------------------------------------------------------------------------------------
# Overarching assumptions
1. The handle is a lower case concatenation of the first-name and the last-name. If this handle is already taken, an integer is concatenated to the end, ascending from 1.
2. Assume that names that are purely whitespaces are not valid.

### Channel functions:
The main assumption is that we only need to register the user once, and afterwards, we can log them in each time we test a certain function, that is, we assume that there is a database storing login details 

#### channel_invite(token, channel_id, u_id):
1. Assumes that channel_detail behaves as expected.
2. Users are appended to the end of the list of all_members when added.

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
4. Assuming that the function throws an some sort of exception if the last user on a private channel tries to leave as there would be no one left to invite others

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
1. Assuming that messages that are empty strings or white spaces are not allowed, since 'message_edit' deletes
    messages which have been edited to empty strings.
2. Assuming that an invalid channel_id will also throw some error

#### message_remove():
1. Assuming that 'message no longer exists' means that the message_id is not valid
2. Assuming that removing a message means it will no longer be displayed when channel_messages is called.

#### message_edit():
1. Assuming message_send and message_remove work as intended.
2. Assume it is impossible for a user to use the edit message function if no messages have been sent.
3. The search function behaves as described.
4. channel_join and channel_leave work as per the spec.
5. A user that has not joined a channel cannot see or access the messages in that channel, hence cannot edit the messages at all.

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
3. Assume that auth_logout behaves as expected.

#### user_profile_setname(token, name_first, name_last):
1. Assume that the 'user_profile' function behaves correctly.
2. Assume that 'name_*' containing white spaces only is invalid.
3. First- and last-names can be more than one word each. E.g. Sue Anne is a valid name_first.
4. Names can contain and consist only of symbols.
5. Assume that names can contain whitespaces as long as they also contain other characters.

#### user_profile_setemail(token, email):
1. Assume that the email provided exists.
2. Assumes that the validity of the email is accurately determined by is_valid_email.py
3. Assumes that if an InputError is thrown for a non-unique email, then the authorised user's email remains unchanged

#### user_profile_sethandle(token, handle_str):
1. Assumes that handles may contain upper case letters, numbers and symbols.

#### users_all(token)
1. Assumes that returned dictionaries will be of the following form:
	```python
	{
		'users': [
            {
                'u_id': 1,
                'email': 'cs1531@cse.unsw.edu.au',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'hjacobs',
            },
        ],
    }
	```
2. Assumes users appear in the user dictionary in the order in which they were registered.
3. Assumes that handle_str is generated as expected.

#### search(token, query_str):
1. Assume that valid search strings are no longer than 1000 characters in length 
2. Assume that the list 'messages' orders the results from oldest to newest (e.g. time_created in ascending order) 
3. Assume that empty search strings return empty 'messages' list

### Standup functions:

#### standup_active(token, channel_id):
1. Assume that any user in slackr can view if a channel has a standup even if not a member
--------------------------------------------------------
# HTTP wrappers Assumptions

## Channel wrappers
`Overarching assumption is the data in the request is given in json format which contains the following keys:`
1. token
2. channel_id
3. u_id
4. start

## Standup wrappers
`Overarching assumption is that the data in request is given in json format which contains the following keys:`
1. token
2. channel_id
3. length
