'''
The server that handles the routes for slackr
'''
from json import dumps
import sys
from flask import Flask, request
from flask_cors import CORS
from error import InputError

# handles the database and server's state and data
import state

# these are routes imports
from auth_routes import AUTH
from message_routes import MESSAGE
from standup_routes import STANDUP
from other_routes import OTHER
from user_routes import USER
from channels_routes import CHANNELS
from channel_routes import CHANNEL

APP = Flask(__name__)
CORS(APP)


# registering the routes in other files
APP.register_blueprint(OTHER)
APP.register_blueprint(CHANNEL, url_prefix='/channel')
APP.register_blueprint(CHANNELS, url_prefix='/channels')
APP.register_blueprint(AUTH, url_prefix='/auth')
APP.register_blueprint(USER, url_prefix='/user')
APP.register_blueprint(MESSAGE, url_prefix='/message')
APP.register_blueprint(STANDUP, url_prefix='/standup')


def defaultHandler(err):  # pylint: disable=missing-function-docstring
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response


APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })


if __name__ == "__main__":
    state.initialize_state()
    state.DATABASE_UPDATER.start()
    APP.run(port=(int(sys.argv[1]) if len(sys.argv) == 2 else 8080))
