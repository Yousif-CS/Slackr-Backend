'''
This file contains implementations for functions:
- user_profile
- user_profile_setname
- user_profile_setemail
- user_profile_sethandle
- profile_uploadphoto

This script requires that the PIL Module be installed
'''

# pylint: disable=trailing-whitespace

import io
import requests
from PIL import Image
from state import get_store, get_tokens, image_config
from auth import verify_token
from error import InputError, AccessError
from is_valid_email import is_valid_email

OK_STATUS = 200
MIN_NAME_LEN = 1
MAX_NAME_LEN = 50
MIN_HANDLE_LEN = 2
MAX_HANDLE_LEN = 20

def user_profile(token, u_id):
    '''
    Returns profile information about the specified user; specifically, 
    u_id, email, name_first, name_last, handle_str, profile_img_url

    Args:
        token (str): of the user authorising this action
        u_id (int): user ID of the user whose profile information is being sought

    Raises:
        AccessError: if token is invalid

    Returns:
        dictionary: a dictionary containing the 'user' dictionary, which contains
            u_id, email, name_first, name_last, handle_str, profile_img_url
    '''

    # check validity of user's token
    if verify_token(token) is False:
        raise AccessError(description="Invalid token")

    # check that the u_id of the user whose information the authorised user wants to access is valid
    data = get_store()
    return {'user': data.users.user_details(u_id)}


def user_profile_setname(token, name_first, name_last):
    '''
    Updates the authorised user's first name and last name.

    Args:
        token (str): of the user authorising this action
        name_first (str): user's new first name (1-50 char)
        name_last (str): user's new last name (1-50 char)

    Raises:
        AccessError: if token is invalid
        InputError: if either name_first or name_last is shorter than 1 char or longer than 50 char
    '''

    # verify token is valid
    if verify_token(token) is False:
        raise AccessError(description="Invalid token")

    # verify that changes to name are allowed
    if len(name_first) < MIN_NAME_LEN or len(name_last) < MIN_NAME_LEN \
            or len(name_first) > MAX_NAME_LEN or len(name_last) > MAX_NAME_LEN:
        raise InputError(description="Names must be between 1 and 50 characters long inclusive.")
    # another verification that names are not just spaces
    if name_first.isspace() or name_last.isspace():
        raise InputError(
            description="Names cannot exclusively contain whitespaces.")

    # modify name_first and name_last in the database as per the user's changes
    u_id = get_tokens()[token]
    data = get_store()
    data.users.set_first_name(u_id, name_first)
    data.users.set_last_name(u_id, name_last)


def user_profile_setemail(token, email):
    '''
    Updates the authorised user's email address.

    Args:
        token (str): of the user authorising this action
        email (str): user's new email address

    Raises:
        AccessError: if token invalid
        InputError:
            if email invalid as determined by is_valid_email module
            if email is already being used by another user
    '''

    # verify that the token is valid
    if verify_token(token) is False:
        raise AccessError(description="Invalid token")

    # InputError if email not valid
    if is_valid_email(email) is False:
        raise InputError(description="Input is not a valid email")

    u_id = get_tokens()[token]
    data = get_store()

    # InputError if email not unique
    # Allow if the user is simply changing their email to their current email again.
    if data.users.email_used(email):
        raise InputError(description="this email is already being used by another user")

    # Change the user's email in the STORE databas if the above hurdles are passed
    data.users.set_email(u_id, email)


def user_profile_sethandle(token, handle_str):
    '''
    Updates the authorised user's handle.

    Args:
        token (str): of the user authorising this action
        handle_str (str): user's new handle

    Raises:
        AccessError: if token not valid
        InputError:
            if handle_str not between 2 and 20 characters inclusive
            if handle_str not unique to user
    '''

    # verify the token is valid
    if verify_token(token) is False:
        raise AccessError(description="Invalid token")

    # verify the new handle_str is of the correct length
    if len(handle_str) < MIN_HANDLE_LEN:
        raise InputError(
            description="handle_str too short - it must be between 2 and 20 characters inclusive")
    if len(handle_str) > MAX_HANDLE_LEN:
        raise InputError(
            description="handle_str too long - - it must be between 2 and 20 characters inclusive")

    u_id = get_tokens()[token]
    data = get_store()

    # verify the new handle_str is unique
    # allow the "change" if the authorised user's new handle_str is identical to their old one.
    if data.users.get_handle(u_id) != handle_str and not data.users.handle_unique(handle_str):
        raise InputError(description="new handle_str not unique to this user")

    # change the handle_str in the database
    data.users.set_handle(u_id, handle_str)

def profile_uploadphoto(token, url, box):
    '''
    Crops a given image from a url and stores it in the database
    Arguments: token, image url, coordinates to be cropped
    Returns: nothing, but with url for the cropped image stored in the users details
    '''
    # # verify that the token is valid
    # if verify_token(token) is False:
    #     raise AccessError(description="Invalid token")

    # preparing the coordinates
    x_start, y_start, x_end, y_end = box

    # getting the image
    response = requests.get(url)
    # checking the image url given is valid
    if response.status_code != OK_STATUS:
        raise InputError(description='Cannot open image')

    # getting the image
    image = Image.open(io.BytesIO(response.content))

    # making sure the image type is JPG
    if image.format != 'JPEG':
        raise InputError('Invalid image format')

    # checking the supplied coordinates are valid
    img_width, img_height = image.size
    if x_start < 0 or y_start < 0 or \
       x_end > img_width or y_end > img_height:
        raise InputError('Invalid crop coordinates')

    # crop the image
    cropped_img = image.crop(box)
    # get the database
    data = get_store()
    # saving the image into the database
    u_id = get_tokens()[token]
    # pylint: disable=global-statement
    cropped_img.save(f"{image_config()['path']}/{u_id}.jpg")
    data.users.set_image(u_id)
