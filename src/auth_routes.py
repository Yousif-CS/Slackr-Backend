'''
This module contains all the routes for auth functionalities
'''

from auth import auth_register, auth_login, auth_logout
from server import APP
from json import dumps 
from flask import Flask, request 

@APP.route('/auth/register', methods=['POST'])
def create_user(): 
    details = request.get_json()
    reg_info = auth_register(details['email'], details['password'], details['name_first'], details['name_last'])
    return dumps(reg_info)

@APP.route('/auth/login', methods=['POST'])
def connect(): 
    details = request.get_json()
    login_info = auth_login(details['email'], details['password'])
    return dumps(login_info)

@APP.route('/auth/logout', methods= ['POST'])
def disconnect(): 
	details = request.get_json()
	successful = auth_logout(details['token'])
	return dumps(successful)
	
	

	

	
    






    
    
