# This file contains assumptions made while testing backend functions
===================================================================================================
## The structure of this file involves functions as headers and the assumptions as bullet points
---------------------------------------------------------------------------------------------------
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

