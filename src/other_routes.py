'''
This module contains all the routes for miscellaneous functionalities
'''

import json
import io
from flask import request, Blueprint, send_file
from PIL import Image
import other
from error import RequestError

OTHER = Blueprint('other', __name__)


def serve_img(img):
    '''
    A function that loads the image to send
    Sourced from:
    https://stackoverflow.com/questions/7877282/how-to-send-image-generated-by-pil-to-browser
    Input: an Image object
    '''
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

@OTHER.route('/admin/userpermission/change', methods=['POST'])
def u_per_change():
    '''
    A wrapper for userpermission_change
    '''
    payload = request.get_json()

    if not payload['token'] or not payload['u_id'] or not payload['permission_id']:
        raise RequestError(description=f"Missing data in request body")

    other.userpermission_change(
        payload['token'], int(payload['u_id']), int(payload['permission_id']))
    return json.dumps({})


@OTHER.route('/admin/user/remove', methods=['DELETE'])
def user_remove():
    '''
    A wrapper for other.user_remove()
    '''
    token = request.args.get('token')
    u_id = request.args.get('u_id')
    if not token or not u_id:
        raise RequestError(description='Missing data in request body')

    other.user_remove(token, int(u_id))
    return json.dumps({})

@OTHER.route('/users/all', methods=['GET'])
def users_all():
    '''
    Wrapper for users_all
    '''
    token = request.args.get('token')

    if not token:
        raise RequestError(description="Missing data in request body")

    every_user = other.users_all(token)
    return json.dumps(every_user)


@OTHER.route('/search', methods=['GET'])
def search():
    '''
    Wrappers for search
    '''
    token = request.args.get('token')
    query_str = request.args.get('query_str')

    if not token or (not query_str and not query_str == ""):
        raise RequestError(description="Missing data in request body")

    matching_msgs = other.search(token, query_str)
    return json.dumps(matching_msgs)


@OTHER.route('/workspace/reset', methods=['POST'])
def reset():
    '''
    A route to reset the whole server database
    '''
    other.workspace_reset()
    return json.dumps({})

@OTHER.route('/imgurl', methods=['GET'])
def fetch_image():
    '''
    A route to fetch a certain image given the url
    '''
    path = request.args.get('path')
    print('THE PATH IS: ', path)
    img = Image.open(path, 'r')
    return serve_img(img)
    