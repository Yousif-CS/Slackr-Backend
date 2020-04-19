'''
The server that handles the routes for slackr
'''
from json import dumps
import sys
import time
from multiprocessing import Process
import json
import requests
from flask import Flask
from flask_cors import CORS

# Has database classes and functions that handle server's state and data
import state

# these are routes imports
from auth_routes import AUTH
from message_routes import MESSAGE
from standup_routes import STANDUP
from other_routes import OTHER
from user_routes import USER
from channels_routes import CHANNELS
from channel_routes import CHANNEL


class CustomFlask(Flask):
    '''
    A simple abstraction over Flask that allows to add a callback after
    the initialization of the APP
    '''

    def run(self, host=None, port=None, debug=None,
            load_dotenv=True, **options):
        try:
            state.initialize_state()
            super(
                CustomFlask,
                self).run(
                host=host,
                port=port,
                debug=debug,
                load_dotenv=load_dotenv,
                **options)
            UPDATE_PROCESS.daemon = True
            UPDATE_PROCESS.start()
            UPDATE_PROCESS.join()
        except KeyboardInterrupt:
            state.update_database()
            UPDATE_PROCESS.terminate()
            print('Exiting server...')


APP = CustomFlask(__name__)
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

# Database update route
@APP.route("/update", methods=['PUT'])
def update():
    '''
    A regular database updater that is invoked via a seperate process http request
    '''
    state.update_database()
    return json.dumps({})


def update_timer():
    '''
    An HTTP request to update the database every n seconds
    '''
    try:
        while True:
            time.sleep(state.SECONDS_TO_UPDATE)
            requests.put(f"{state.HOST}:{state.PORT}/update")
    except KeyboardInterrupt:
        pass


UPDATE_PROCESS = Process(target=update_timer)


def main():
    '''
    The main function that runs on the command `pytest3 server.py [PORT]`
    '''
    print('Server Initiated!')
    state.PORT = int(sys.argv[1]) if len(sys.argv) == 2 else 8080
    APP.run(port=state.PORT)


if __name__ == "__main__":
    main()
