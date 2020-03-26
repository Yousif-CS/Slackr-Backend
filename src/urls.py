'''
Module contains urls used for testing
'''

HOSTNAME = '127.0.0.1'
PORT = 5000

RESET_URL = f"http://{HOSTNAME}:{PORT}/workspace/reset"

#auth urls
REGISTER_URL = f"http://{HOSTNAME}:{PORT}/auth/register"
LOGIN_URL = f"http://{HOSTNAME}:{PORT}/auth/login"
LOGOUT_URL = f"http://{HOSTNAME}:{PORT}/auth/logout"

#channel urls
INVITE_URL = f"http://{HOSTNAME}:{PORT}/channel/invite"
CHANNEL_DETAILS_URL = f"http://{HOSTNAME}:{PORT}/channel/details"
MESSAGES_URL = f"http://{HOSTNAME}:{PORT}/channel/messages"
JOIN_URL = f"http://{HOSTNAME}:{PORT}/channel/join"
LEAVE_URL = f"http://{HOSTNAME}:{PORT}/channel/leave"
ADDOWNER_URL = f"http://{HOSTNAME}:{PORT}/channel/addowner"
REMOVEOWNER_URL = f"http://{HOSTNAME}:{PORT}/channel/removeowner"

#channels urls
CHANNELS_CREATE_URL = f"http://{HOSTNAME}:{PORT}/channels/create"

#message urls
SEND_URL = f"http://{HOSTNAME}:{PORT}/message/send"
