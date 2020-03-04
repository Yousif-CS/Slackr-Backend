import pytest 
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

		auth_register('@gmail.com', 'passwordian10', 'Max' 'Smith')

		auth_register('@gmail.com', 'passwordian10', 'Max' 'Smith')


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
		
	
	
	 

