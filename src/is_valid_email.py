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
        return True
          
    else:  
        return False

if __name__ == "__main__":
    print(is_valid_email("kenli@gmail.com"))
    print(is_valid_email("joshua_wang2@gmail.cc"))
    print(is_valid_email("joshua.wa-ng_23@mail-archive.com"))
    print(is_valid_email("kenligordon@gmail.com"))
    print(is_valid_email("kenligordon1@gmail1.com"))

    print("Below should be invalid")

    print(is_valid_email("ken-@gmail.ab"))
    print(is_valid_email("ken.-li@gmail.ab"))
    print(is_valid_email(".ken@gmail.ab"))
    print(is_valid_email("ken#li@gmail.ab"))
    print(is_valid_email("ken@gmail.a"))
    print(is_valid_email("kenli@google#mail.com"))
    print(is_valid_email("kenli@google.mail"))
    print(is_valid_email("ken@gmail..com"))
    