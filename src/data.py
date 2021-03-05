# File containing all of the data variables

'''
Two variables:

users (list):
    each element of list is a user dictionary containing:
        user_id
        first_name
        last_name
        email
        password

channels (list):
    each element of list is a channel dictionary containing:
        channel_id
        is_public (bool)
        channel_name
        owner members (list of user_id's)
        all members (list of user_id's)
'''
#* Like so
"""
users = [
    {
        'user_id': ____,
        'first_name': ____,
        'last_name': ____,
        'email': ____,
        'password': ____,
        'handle_string': ____,
    }
]

channels = [
    {
        'channel_id': ____,
        'is_public': ____,
        'channel_name': ____,
        'owner_members': [],
        'all_members': [],
    }
]
"""

user = []
channels = []