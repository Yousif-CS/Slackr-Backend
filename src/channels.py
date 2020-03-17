from server import get_store, get_tokens
from auth import verify_token
from error import InputError

def channels_list(token):
    '''
    Input: token
    Output: dictionary of channels (and associated details) that the authorised user is part of
    {channels} = {[
        {
            'channel_id': '1',
            'name': 'first_channel_name'
        },
        {
            'channel_id': '2',
            'name': 'another channel name'
        },
    ]}
    '''
    # verify the user
    if verify_token(token) is False:
        raise InputError(description='Invalid token')

    # from token, get list of channels user is part of
    data = get_store()
    # getting id of the user
    # get_tokens() should return a dictionary where token key corresponds to that user's id
    u_id = get_tokens()[token]

    # return details about all channels the user is part of
    channels_dict = {}
    for ids in data['Users'][u_id]['channels']:
        channels_dict['channels'].append({
            'channel_id': ids,
            'name': data['Channels'][ids]['name'],
        })
    return channels_dict
