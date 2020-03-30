from werkzeug.exceptions import HTTPException


class AccessError(HTTPException):
    code = 400
    message = 'No message specified'


class InputError(HTTPException):
    code = 400
    message = 'No message specified'


class RequestError(HTTPException):
    code = 400
    message = 'Missing data in request'
