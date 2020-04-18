'''
The server that handles the routes for slackr
'''
from json import dumps
import sys
import time
import atexit
from multiprocessing import Process
import requests
import json
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



class CustomFlask(Flask):
    def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
        # if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
        #     with self.app_context():
        #         do_something()
        try:
            state.initialize_state()
            super(CustomFlask, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)
            UPDATE_PROCESS.daemon = True
            # atexit.register(state.update_database)
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

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

# Database update route
@APP.route("/update", methods=['PUT'])
def update():
    state.update_database()
    return json.dumps({})

#DATABASE_UPDATER = state.StateTimer(state.SECONDS_TO_UPDATE, state.update_database)

# def run_updater():
#     '''
#     a function that initializes the database updater in parallel
#     '''
#     DATABASE_UPDATER.run()

#A timer that sends http requests to update database
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
UPDATE_PROCESS.daemon = True




@APP.route('/ProcessRun', methods=['PUT'])
def fork_process():
    print('Forked Process!')
    state.initialize_state()
    UPDATE_PROCESS.daemon = True
    UPDATE_PROCESS.start()
    UPDATE_PROCESS.join()
    
def fork_request():
    '''
    Sends a request to the server to initialize the database updater
    '''
    try:
        requests.put(f"{state.HOST}:{state.PORT}/ProcessRun", timeout=0.00000001)
    except requests.exceptions.ReadTimeout:
        print('Request timeout')
        pass

def main():
    print('Server Initiated!')
    #state.PORT = int(sys.argv[1]) if len(sys.argv) == 2 else 8080
    APP.run(port=state.PORT)


def initialize():
    try:
        state.initialize_state()
        UPDATE_PROCESS.start()
        UPDATE_PROCESS.join()
    except KeyboardInterrupt:
        UPDATE_PROCESS.terminate()
    finally:
        state.update_database()

#APP.before_first_request(initialize)

if __name__ == "__main__":
    main()
