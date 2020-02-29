This file contains assumptions made while testing backend functions
===================================================================
The structure of this file involves functions as headers and the assumptions as bullet points
------------------------------------------------------------------
# H3 Channel functions:

# H4 channels_messages():
1. Assuming that the email addresses provided exists for registration
2. Assuming that 'owner' in this context refers only to a channel owner but not workspace owner as a global permission 
3. Assuming big ints such as 123123 are considered invalid channel id
4. Assuming 'I am an invalid token' string to be an invalid token
5. Assuming the function throws an 'AccessError' exception when dealing with invalid tokens

# H4 channel_leave():
3. Assuming big ints such as 123123 are considered invalid channel id
4. Assuming 'I am an invalid token' string to be an invalid token
5. Assuming the function throws an 'AccessError' exception when dealing with invalid tokens

# H4 channel_join():

# H4 channel_addowner():

# H4 channel_removeowner():