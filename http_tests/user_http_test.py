import pytest
import requests
import json
from src.config import url
from src.error import AccessError, InputError
from src.user import user_profile_v2, user_setname_v2, user_setemail_v2, user_sethandle_v2, users_all
from src.auth import auth_register_v2, auth_login_v2
from src.other import clear_v1, SECRET
from jwt import encode


@pytest.fixture
def user1():
    requests.delete(f"{url}clear/v1")    
    response = requests.post(f"{url}auth/register/v2", json={
        "email": "caricoleman@gmail.com",
        "password": "1234567",
        "name_first": "cari",
        "name_last": "coleman"
    })
    return response.json()

#* Fixture that registers a second user
@pytest.fixture
def user2():
    response = requests.post(f"{url}auth/register/v2", json={
        "email": "ericamondy@gmail.com",
        "password": "1234567",
        "name_first": "erica",
        "name_last": "mondy"
    })
    return response.json()

# tests the case when the provided token contains an invalid user id    
def test_http_user_profile_invalid_uid(user1):
    requests.post(f"{url}auth/login/v2", json={'email': "caricoleman@gmail.com", "password": "1234567"})
    token = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    response = requests.get(f"{url}user/profile/v2", params={'token': token, 'u_id': 1})
    assert response.status_code == 400

# tests that set name changes the users first and last names to the inputted first and last names 
# where both the first and last names are being changed
def test_http_user_setname_valid(user1):
    requests.post(f"{url}auth/login/v2", json={'email': "caricoleman@gmail.com", "password": "1234567"})
    token = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    response_1 = requests.put(f"{url}user/profile/setname/v2", json={'token': token, 'name_first': 'kari', 'name_last': 'koleman'})
    payload_1 = response_1.json()
    assert payload_1 == {}
    response_2 = requests.get(f"{url}user/profile/v2", params={'token': token, 'u_id': 0})
    payload_2 = response_2.json()
    assert payload_2 == { 
        'user':
            {
            'u_id': 0, 
            'email': "caricoleman@gmail.com", 
            'name_first': 'kari', 
            'name_last': 'koleman', 
            'handle_str': 'caricoleman'
            }
    }

# tests for the case where the inputted first name exceeds the 50 character limit
def test_http_user_setname_invalid_long_first_name(user1):
    requests.post(f"{url}auth/login/v2", json={'email': "caricoleman@gmail.com", "password": "1234567"})
    token = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    response = requests.put(f"{url}user/profile/setname/v2", json={'token': token, 'name_first': 'kariiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii', 'name_last': 'koleman'})
    assert response.status_code == 400

# tests for the case where the inputted last name exceeds the 50 character limit
def test_http_user_setname_invalid_long_last_name(user1):
    requests.post(f"{url}auth/login/v2", json={'email': "caricoleman@gmail.com", "password": "1234567"})
    token = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    response = requests.put(f"{url}user/profile/setname/v2", json={'token': token, 'name_first': 'kari', 'name_last': 'kolemaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaan'})
    assert response.status_code == 400

# tests for the case where the inputted first name is empty
def test_http_user_setname_invalid_no_first_name(user1):
    requests.post(f"{url}auth/login/v2", json={'email': "caricoleman@gmail.com", "password": "1234567"})
    token = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    response = requests.put(f"{url}user/profile/setname/v2", json={'token': token, 'name_first': '', 'name_last': 'koleman'})
    assert response.status_code == 400    

# tests for the case where the inputted last name is empty
def test_http_user_setname_invalid_no_last_name(user1):
    requests.post(f"{url}auth/login/v2", json={'email': "caricoleman@gmail.com", "password": "1234567"})
    token = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    response = requests.put(f"{url}user/profile/setname/v2", json={'token': token, 'name_first': 'kari', 'name_last': ''})
    assert response.status_code == 400    

# tests that set email changes the users email to the inputted email
def test_http_user_setemail_valid(user1):
    requests.post(f"{url}auth/login/v2", json={'email': "caricoleman@gmail.com", "password": "1234567"})
    token = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    response_1 = requests.put(f"{url}user/profile/setemail/v2", json={'token': token, 'email': 'karicoleman@gmail.com'})
    payload_1 = response_1.json()
    assert payload_1 == {}
    response_2 = requests.get(f"{url}user/profile/v2", params={'token': token, 'u_id': 0})
    payload_2 = response_2.json()
    assert payload_2 == {
        'user':
        {
        'u_id': 0, 
        'email': "karicoleman@gmail.com", 
        'name_first': 'cari', 
        'name_last': 'coleman', 
        'handle_str': 'caricoleman'
        }
    }

# tests the case where the inputted email is of invalid format
def test_http_user_setemail_invalid_email(user1):
    requests.post(f"{url}auth/login/v2", json={'email': "caricoleman@gmail.com", "password": "1234567"})
    token = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    response = requests.put(f"{url}user/profile/setemail/v2", json={'token': token, 'email': 'karicoleman.com'})
    assert response.status_code == 400    

# tests the case where the inputted email is already being used by another registerd user
def test_http_user_setemail_invalid_email_in_use(user1,user2):
    requests.post(f"{url}auth/login/v2", json={'email': "caricoleman@gmail.com", "password": "1234567"})
    token_1 = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    requests.post(f"{url}auth/login/v2", json={'email': "ericamondy@gmail.com", "password": "1234567"})
    token_2 = encode({'session_id': 1, 'user_id': 1}, SECRET, algorithm='HS256')
    requests.put(f"{url}user/profile/setemail/v2", json={'token': token_1, 'email': 'karicoleman.com'})
    response = requests.put(f"{url}user/profile/setemail/v2", json={'token': token_2, 'email': 'karicoleman.com'})
    assert response.status_code == 400    

# tests that set handle changes the users handle string to the inputted handle string
def test_http_user_sethandle_valid(user1):
    requests.post(f"{url}auth/login/v2", json={'email': "caricoleman@gmail.com", "password": "1234567"})
    token = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    response_1 = requests.put(f"{url}user/profile/sethandle/v2", json={'token': token, 'handle_str': 'karikoleman'})
    payload_1 = response_1.json()
    assert payload_1 == {}
    response_2 = requests.get(f"{url}user/profile/v2", params={'token': token, 'u_id': 0})
    payload_2 = response_2.json()
    assert payload_2 == {
        'user':
        {
        'u_id': 0, 
        'email': "caricoleman@gmail.com", 
        'name_first': 'cari', 
        'name_last': 'coleman', 
        'handle_str': 'karikoleman'
        }
    }

# tests for the case when the inputted handle string has less than 3 characters
def test_http_user_sethandle_invalid_short_handle(user1):
    requests.post(f"{url}auth/login/v2", json={'email': "caricoleman@gmail.com", "password": "1234567"})
    token = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    response = requests.put(f"{url}user/profile/sethandle/v2", json={'token': token, 'handle_str': 'cc'})
    assert response.status_code == 400    

# tests for the case when the inputted handle string exceeds the 20 character limit
def test_http_user_sethandle_invalid_long_handle(user1):
    requests.post(f"{url}auth/login/v2", json={'email': "caricoleman@gmail.com", "password": "1234567"})
    token = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    response = requests.put(f"{url}user/profile/sethandle/v2", json={'token': token, 'handle_str': 'cariiiiiiiiiiiiiiiiii'})
    assert response.status_code == 400    

# tests for the case when the inputted handle string is already being used by another user
def test_http_user_sethandle_invalid_handle_in_use(user1,user2):
    requests.post(f"{url}auth/login/v2", json={'email': "caricoleman@gmail.com", "password": "1234567"})
    token_1 = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    response_1 = requests.put(f"{url}user/profile/sethandle/v2", json={'token': token_1, 'handle_str': 'kari'})
    payload_1 = response_1.json()
    assert payload_1 == {}
    requests.post(f"{url}auth/login/v2", json={'email': "ericamondy@gmail.com", "password": "1234567"})
    token_2 = encode({'session_id': 1, 'user_id': 1}, SECRET, algorithm='HS256')
    response_2 = requests.put(f"{url}user/profile/sethandle/v2", json={'token': token_2, 'handle_str': 'kari'})
    assert response_2.status_code == 400

# tests the return value of users_all for when two users are registered
def test_http_users_all_valid(user1,user2):
    requests.post(f"{url}auth/login/v2", json={'email': "caricoleman@gmail.com", "password": "1234567"})
    token = encode({'session_id': 1, 'user_id': 0}, SECRET, algorithm='HS256')
    requests.post(f"{url}auth/login/v2", json={'email': "ericamondy@gmail.com", "password": "1234567"})
    response = requests.get(f"{url}users/all/v1", params={'token': token})
    payload = response.json()
    assert payload == {
            'users':
            [{
            'u_id': 0, 
            'email': "caricoleman@gmail.com", 
            'name_first': 'cari', 
            'name_last': 'coleman', 
            'handle_str': 'caricoleman'
            },
            {
            'u_id': 1, 
            'email': "ericamondy@gmail.com", 
            'name_first': 'erica', 
            'name_last': 'mondy', 
            'handle_str': 'ericamondy'
            }]
    } 
    
def test_http_users_stats_v1(user1, user2, user3, user4):

