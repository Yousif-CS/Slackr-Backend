'''
This module contains all the routes for auth functionalities
'''
from flask import Flask, request 
from server import APP
from auth import auth_register, auth_login, auth_logout
from json import dumps

@APP.route('/auth/register', methods=['POST'])
def create_user(): 
    ''' 
    A route to register a user
    '''
    payload = request.get_json()
    if not payload['email'] or not payload['password'] or not payload['name_first'] or not payload['name_last']:
        raise RequestError(description=f"Missing data in request body")

    reg_info = auth_register(payload['email'], payload['password'], payload['name_first'], payload['name_last'])
    return dumps({})


@APP.route('/auth/login', methods=['POST'])
def connect():
    '''
    A route to login a user
    ''' 
    payload = request.get_json()
    if not payload['email'] or not payload['password']:
        raise RequestError(description=f"Missing data in request body")
        
    login_info = auth_login(details['email'], details['password'])
    return dumps(login_info)

@APP.route('/auth/logout', methods= ['POST'])
def disconnect(): 
    ''' 
    A route to logout the user
    '''
    payload = request.get_json()
    if not payload['token']:
        raise RequestError(description=f"Missing data in request body")
    successful = auth_logout(payload['token'])
    return dumps(successful)
	
	

	

	
    






    
    
