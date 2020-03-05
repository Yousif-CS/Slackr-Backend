import pytest 
import user 
from auth import auth_register, auth_login, auth_logout 
from error import InputError 

#Test Valid Registration details 
def test_register(): 
	credentials = auth_register('max.smith@gmail.com', 'great_password101', 'Max', 'Smith') 

#Invalid email 
def test_register_invalid_email():
	with pytest.raises(InputError) as e:
		auth_register('maxsmith', 'cryptic_password#1500', 'Max', 'Smith')

#Only domain given for email 
def test_register_wrong_email():
	with pytest.raises(InputError) as e:
		auth_register('@gmail.com', 'passwordian1', 'Max' 'Smith')

#Password is too short 
def test_register_invalid_password():
	with pytest.raises(InputError) as e: 
		auth_register('max.smith@gmail.com', 'abc', 'Max', 'Smith') 

#First name is too many characters 
def test_register_long_first_name():
	with pytest.raises(InputError) as e: 
		auth_register('max.smith@gmail.com', 'great_password101', 'c' * 51, 'Smith') 

#Last name is too many characters 
def test_register_long_last_name(): 
	with pytest.raises(InputError) as e:
		auth_register('max.smith@gmail.com', 'great_password101', 'Max', 'zz' * 26) 

#User already exists 
def test_register_existing_user(): 
	original_user = auth_register('max.smith@gmail.com', 'great_password101', 'Max', 'Smith') 
	
	with pytest.raises(InputError) as e:
		auth_register('max.smith@gmail.com', 'great_password101', 'Max', 'Smith') 


#Login tests 


#Valid user logging in 
def test_login(): 
	user = auth_register('max.smith@gmail.com', 'great_password101', 'Max', 'Smith')  
	
	user_logging_in = auth_login('max.dsmith@gmail.com', 'great_password101') 
		
	assert user['u_id'] == user_logging_in['u_id'] 


#Wrong password given

def test_login_password(): 
	user = auth_register('max.smith@gmail.com', 'great_password101', 'Max', 'Smith')  
	
	with pytest.raises(InputError) as e:
		user_loggingin = auth_login('max.smith@gmail.com', 'poor_password') 

#No users registered with email 

def test_login_no_user():

	first_user = auth_register('max.smith@gmail.com', 'great_password101', 'Max', 'Smith')  
	
	scnd_user = auth_register('bob99@unsw.edu.au', '45&*ght', 'Bob', 'Johnson') 
		
	third_user = auth_register('kate58@bigpond.com', 'secret101', 'Kate' , 'Perkins') 
	
	with pytest.raises(InputError) as e:
		auth_login('linda70@gmail.com' , 'let_me_in') 

#Using user's token the logout is successful 
def test_logout_success(): 
	
	user = auth_register('max.smith@gmail.com', 'great_password101', 'Max', 'Smith')  
	
	user_logging_in = auth_login('max.dsmith@gmail.com', 'great_password101') 

	assert user['u_id'] == user_logging_in['u_id'] 
	
	user_token = user_logging_in['token'] 
	message = auth_logout(user_token) 
	
	assert message['is_success'] == True 


#Token is not valid for a user 
def test_logout_unsuccessful(): 
	user = auth_register('max.smith@gmail.com', 'great_password101', 'Max', 'Smith')  
	
	user_logging_in = auth_login('max.dsmith@gmail.com', 'great_password101') 
	
	assert user['u_id'] == user_logging_in['u_id'] 
	user_token = user_logging_in['token'] 
	
	rand_token = 'Not a valid token'
		
	assert user_token != rand_token 
	message = auth_logout(rand_token) 
	assert message['is_success'] == False 
	


#A logged out user trying to join a channel 
def test_logout_join_fails(): 
	user = auth_register('max.smith@gmail.com', 'great_password101', 'Max', 'Smith')  
	
	user_logging_in = auth_login('max.dsmith@gmail.com', 'great_password101') 

	assert user['u_id'] == user_logging_in['u_id'] 
	
	user_token = user_logging_in['token'] 
	message = auth_logout(user_token) 
	
	assert message['is_success'] == True 
	
	with pytest.raises(InputError) as e: 
		channel_join(user_token, 1)
	
		
	
	

		
	
	
	

 
	




 
	
	
		
	
	
	 

