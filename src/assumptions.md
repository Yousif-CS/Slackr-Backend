This file contains assumptions made while testing backend functions
===================================================================
The structure of this file involves functions as headers and the assumptions as bullet points
------------------------------------------------------------------
# H3 Channel functions:

# H4 channels_messages():
1. Assuming that the email addresses provided exists for registration
2. Assuming that 'owner' in this context refers only to a channel owner but not workspace owner as a global permission 
3. Assuming big ints such as 123123 are considered invalid channel id
# H4 channel_leave():
3. Assuming big ints such as 123123 are considered invalid channel id
# H4 channel_join():

# H4 channel_addowner():

# H4 channel_removeowner():