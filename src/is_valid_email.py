""" Checks whether an email is valid. Code sourced entirely from 
https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
with minor modifications."""
import re 
  
# Make a regular expression 
# for validating an Email 
regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
      
# Define a function for 
# for validating an Email 
def is_valid_email(email):  
  
    # pass the regualar expression 
    # and the string in search() method 
    if(re.search(regex,email)):  
        print("valid")
          
    else:  
        print("invalid")

if __name__ == "__main__":
    is_valid_email("kenli@gmail.com")
    is_valid_email("joshua_wang2@gmail.com")
    is_valid_email("joshua.wang_2@gmail.com")
    is_valid_email("")
    is_valid_email("")
    is_valid_email("")
    is_valid_email("")
    is_valid_email("")
    is_valid_email("")
    is_valid_email("")