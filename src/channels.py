from server import get_store, get_tokens
from auth import verify_token
from error import InputError

def channels_list(token):
    '''
    Input: token
    Output: list of channels (and associated details) that the authorised user is part of
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

    # get database
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


def channels_listall(token):
    '''
    Input: token
    Output: list of ALL channels in slackr
    '''
    # verify the user
    if verify_token(token) is False:
        raise InputError(description='Invalid token')

    # get database
    data = get_store()

    # return all existing channels
    all_channels_dict = {}
    for ids in data['Channels']:
        all_channels_dict['channels'].append({
            'channel_id': ids,
            'name': data['Channels'][ids]['name'],
        })
    return all_channels_dict

def channels_create(token, name, is_public):
    '''
    Input: token, name, is_public status
    Output: {channel_id}, creates a new channel with the input name and public / private
    '''
    # verify the user
    if verify_token(token) is False:
        raise InputError(description='Invalid token')

    # get database
    data = get_store()
    # getting user id from token
    u_id = get_tokens()[token]

    # check if name is valid
    if not isinstance(name, str) or len(name) > 20:
        raise InputError(description='Invalid channel name')

    # check if is_public is correct type
    if not isinstance(is_public, bool):
        raise InputError(description='Invalid channel status')

    # assigning new id for channel
    # if no channels exist, assign 1 as new id; otherwise assign max_id_size + 1
    if len(channels_listall(token)['channels']) == 0:
        new_id = 1
    else:
        new_id = max([i for i in data['Channels']]) + 1

    # updating database:
    # 1. adding new key value pair into data.Channels
    data['Channels'][new_id] = {
        'name': name,
        'all_members': [u_id],
        'owner_members': [u_id],
        'is_priate': not is_public,
        'messages': [],
    }
    # 2. adding new channel id to user info
    data['Users'][u_id]['channels'].append(new_id)

    return {'channel_id': new_id}
