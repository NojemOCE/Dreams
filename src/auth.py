import src.data
from src.error import AccessError, InputError
import re

def auth_login_v1(email, password):
    """ Checks if inputted email is present within the registered users
        If email is present, checks that the inputted password matches the password stored for 
        that particular registered email. 

        Arguments:
            email (str): The email of the user
            password (str): The password of the user

        Exceptions:
            InputError : occurs when the inputted email isn't present within the registered users
            InputError : occurs when the inputted password does not match the password stored for that particular inputted email

        Return Value:
            Returns (dict) containing user_id corresponding to the inputted email and password 

    """
    for user in src.data.users:
        if email == user.get('email') and password == user.get('password'):
            return {
                'auth_user_id': user['user_id'],
            }
    raise InputError    



def auth_register_v1(email, password, name_first, name_last):
    """ With the inputted data (email, password, name_first, name_last), checks whether the format of the data are valid. 
        If the data is valid, inserts (registers) the inputted information into a dictionary containing all users information
        and appends that information onto the user data list. Also creates a formatted handlestring which consists of the users first and last name which has a maximum character length 
        of 20 characters unless there are duplicates. 

        Arguments:
            email (str): The email of the user
            password (str): The password of the user
            name_first (str): The first name of the user
            name_last (str): The last name of the user 

        Exceptions:
            InputError : occurs when the inputted email is not a valid email format
            InputError : occurs when the inputted email has already been used to register another user
            InputError : occurs when the inputted password has a length less than 6 characters
            InputError : occurs when the inputted name_first has a length that does not range between 1 - 50 characters
            InputError : occurs when the inputted name_first has a length that does not range between 1 - 50 characters

        Return Value:
            Returns (dict) containing user_id corresponding to the inputted email, password, name_first and name_last

    """
    #* Storing name_first & name_list so original names 
    #* unaffected by handle generation
    nameF = name_first
    nameL = name_last

    # setting all characters to lowercase
    name_first = name_first.lower()
    name_last = name_last.lower()

    # removing whitespace from name_first and name_last
    name_first = name_first.split()
    name_first = ''.join(name_first)
    name_last = name_last.split()
    name_last = ''.join(name_last)
    
    # removing the '@' from name_first and name_last
    name_first = name_first.replace("@", "")
    name_last = name_last.replace("@", "")
    
    # checking if inputted email is valid
    if re.search('^[a-zA-Z0-9]+[\\._]?[a-zA-Z0-9]+[@]\\w+[.]\\w{2,3}$', email):
        pass    
    else: 
        raise InputError

    # checking if inputted email is already being used by another user
    for user in src.data.users:
        if email == user['email']:
            raise InputError

    # checking if password is valid 
    if len(password) < 6:
        raise InputError        

    # checking if first_name ranges between 1 - 50
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError

    # checking if last_name ranges between 1 - 50
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError

    # constructing the user_id from first and last name     
    # checking for total length of first and last name 
    if len(name_first) > 20:
        handle_string = name_first[0:21]
        
    elif len(name_first) + len(name_last) > 20:
        cutoff_len = 20 - len(name_first)
        handle_string = name_first + name_last[0:cutoff_len]
    else:    
        handle_string = name_first + name_last
    
    trailing_int = 0 
    
    # checking for duplicated names   
    for user in src.data.users:
        if handle_string == user['handle_string']:
            if trailing_int > 0:
                handle_string = handle_string[0:-1] + str(trailing_int)
            else:
                handle_string = handle_string + str(trailing_int)
            trailing_int += 1

    user_id = len(src.data.users)

    src.data.users.append({
        'email' : email,
        'password' : password,
        'name_first' : nameF,
        'name_last' : nameL,
        'user_id' : user_id,
        'handle_string' : handle_string,
    })
    return {
        'auth_user_id': user_id,
    }
    
    