'''
This module contains all the routes for auth functionalities
'''

from auth import auth_register, auth_login, auth_logout
from server import APP
from json import dumps 
from flask import Flask, request 

@APP.route('/auth/register', methods=['POST'])
def create_user(): 
    user_input = request.get_json()
    reg_token, user_id = auth_register(user_input['email'], user_input['password'], user_input['name_first'], user_input['name_last'])
    return dumps ({
        'token': reg_token
    })

@APP.route('/auth/login', methods=['POST'])
def connect(): 
    details = request.get_json()
    login_token, user_id = auth_login(details['email'], details['password'])
    return dumps ({
        'token': login_token
    })

@APP.route('/auth/logout', methods= ['POST'])
def disconnect(): 
	details = request.get_josn()
	

	
    






    
    
