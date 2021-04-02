import src.data
from src.error import AccessError, InputError 
from src.channels import channels_listall_v2, channels_list_v2
from src.other import decode, get_channel, get_members, get_user, message_count, push_added_notifications

AuID      = 'auth_user_id'
uID       = 'u_id'
cID       = 'channel_id'
creatorID = 'creator_id'
allMems   = 'all_members'
Name      = 'name'
fName     = 'name_first'
lName     = 'name_last'
chans     = 'channels'
handle    = 'handle_string'
dmID      = 'dm_id'
seshID    = 'session_id'

def channel_invite_v1(token, channel_id, u_id):
    
    '''
    channel_invite_v1 checks if a user is authorised to invite another user to a channel and then automatically adds the
    desired user to the specific channel dictionary within the list contained in "all_members".

    Arguments:
        token (str): JWT containing { u_id, session_id }
        channel_id (int) - The integer id of the channel that we want to invite a user to. Should be present in the channels list.
        u_id (int) - The integer id of a user that the authorised user wants to invite to that specific channel.

    Exceptions:
        InputError - Occurs when the channel_id used as a parameter does not already exist in the channels list.
        InputError - Occurs when the u_id or id of the user that we are trying to invite does not already exist within the users list.
        AccessError - Occurs when the user calling the function is not authorised as a member of that channel, meaning the id is not present in "all_members" within channel dictioanry.

    Return Value:
        Returns an empty list on passing all Exceptions, with changes being made directly to our data.py  
    '''

    auth_user_id, _ = decode(token)

    #check if channel_id is valid
    passed = False
    for check in src.data.channels:
        if check['channel_id'] == channel_id:
            passed = True
            break
    if passed == False:
        raise InputError
    

    # check if user is authorised to invite
    for chans in src.data.channels:
        if chans["channel_id"] == channel_id:
            userAuth = False
            for users in chans["all_members"]:
                if users == auth_user_id:
                    userAuth = True
                    break
            if userAuth == False:
                raise AccessError
                    
    # should check for auth_user_id in channel info first for owners

    get_user(u_id)

    # now searches for channel_id
    for chan in src.data.channels:
        if chan["channel_id"] == channel_id:
            # ensure no duplicates
            chan["all_members"].append(u_id) if u_id not in chan["all_members"] else None
    push_added_notifications(auth_user_id, u_id, channel_id,-1) 
    return {   
    }


def channel_details_v1(token, channel_id):

    '''
    channel_details_v1 calls upon a new copy of the desired channel dictionary that only contains filtered keys and values that is public.
    Does not include private information such as password.
    
    Arguments:
        token (str): JWT containing { u_id, session_id }
        channel_id (int) - The id of the desired channel which we want details of.
    
    Exceptions:
        InputError - Occurs when the channel_id used as a parameter does not already exist in the channels list.
        AccessError - Occurs when the user calling the function is not authorised as a member of that channel, meaning the id is not present in "all_members" within channel dictioanry.
    
    Return Value:
        Returns filteredDetails on succesfully creating a copy of the channel we want, with only the filtered information. The return is a dictionary.
    '''

    auth_user_id, _ = decode(token)

    # check for valid channel
    passed = False
    for check in src.data.channels:
        if check["channel_id"] == channel_id:
            passed = True
            break
    if passed == False:
        raise InputError

    # check if user is authorised for channel
    for chans in src.data.channels:
        if chans["channel_id"] == channel_id:
            userAuth = False
            for users in chans["all_members"]:
                if users == auth_user_id:
                    userAuth = True
                    break
            if userAuth == False:
                raise AccessError
    for details in src.data.channels:
        if details["channel_id"] == channel_id:

            # filteres the information to be displayed
            filteredDetails = dict((item, details[item]) for item in ["name","is_public"] if item in details)

            # takes only user_id, first and last name
            ownmem = []
            for user in details["owner_members"]:
                ownmem.append(get_user(user))
            dictAllOwn = {"owner_members": ownmem}
            filteredDetails.update(dictAllOwn)

            allmem = []
            for user in details["all_members"]:
                allmem.append(get_user(user))
            dictAllMem = {"all_members" : allmem}
            filteredDetails.update(dictAllMem)

    return filteredDetails


def channel_messages_v1(token, channel_id, start):

    '''
    channel_messages_v1 returns up to 50 messages within a specified channel.
    
    Arguments:
        token - The token of the user that is calling the channel details. Must be present within that channel's "all_members".
        channel_id (int) - The id of the desired channel which we want details of.
        start(int) - The index of the message that they wish to start returning from.
    
    Exceptions:
        InputError - Occurs when channel_id is not valid or start is greater than total number of messages in channel.
        AccessError - Occurs when authorised user is not a member of channel with channel_id.
    
    Return Value:
        Returns up to 50 messages alongside a start and and end value.
    '''
    
    # print(auth_user_id)

    print(token)

    decode(token)

    #Handling of input and access errors 
    #Input error: Channel ID is not a valid channel 
    #This is the case
    channelFound = False 
    for channel in src.channels.channels_listall_v2(token)["channels"]:
        if channel_id == channel["channel_id"]:
            channelFound = True
    
    if not channelFound:
        raise InputError


    #Input error: Start is greater than total number of messages in list 
    if start > len(src.data.messages_log):
        raise InputError
    
    #Access error: When auth_user_id is not a member of channel with channel_id 
    userFound = False 
    for channel in src.channels.channels_list_v2(token)["channels"]:
        if channel_id == channel["channel_id"]:
            userFound = True
    
    if not userFound:
        raise AccessError

    
    desired_end = start + 50
    num_of_messages = message_count(channel_id, -1)
        
    if num_of_messages < desired_end:
        desired_end = -1
    messages = []

    for objects in src.data.messages_log:
        if channel_id == objects['channel_id']:
            current_DM = objects.copy()
            del current_DM['channel_id']
            del current_DM['dm_id']
            messages.insert(0,current_DM)

    #Reverse list such that the we have the newest messages at the start and oldest at the end 
    reversed(messages)        

    #Take 50 messages from our start value
    #Chop off all the messages before our start value 
    for _ in range(start):
        messages.pop(0)
    
    while len(messages) > 50:
        messages.pop(-1)
    
    return {
        'messages': messages,
        'start': start,
        'end': desired_end,
    }
    
def channel_leave_v1(token, channel_id):
    '''
    Takes in a user's id and a channel's id and removes that user from that given channel.
    Follows the rules channel_remove_owner_v1 if the user is an owner

    Arguments:
        token        (str) - The JWT containing user_id and session_id of the user that is to leave the channel
        channel_id   (int) - The id of the channel that the user is to leave

    Exceptions:
        InputError - Occurs when the channel_id inputted does not belong to any channel that exists in the database
        AccessError - Occurs when 
                            2) The auth_user_id inputted does not belong to any user that is in the channel

    Return Value:
        Returns an empty list regardless of conditions :)
    '''

    auth_user_id, _ = decode(token)

    # Get the channel directory from data.py
    channelData = get_channel(channel_id)

    # If the user is an owner
    if auth_user_id in channelData['owner_members']:
        channel_removeowner_v1(token, channel_id, auth_user_id)

    # Check if user is in the channel
    if auth_user_id not in channelData['all_members']:
        raise AccessError

    # Time to remove from all_members list
    channelData['all_members'].remove(auth_user_id)
    return {
    }

def channel_join_v1(token, channel_id):
    '''
    Takes in a user's id and a channel's id and adds that user to that given channel.
        --> Specifically adds it to the 'all_members' list in the channel dictionary 
    If the channel is private then the user isn't added. (See more in Exceptions)

    Arguments:
        token        (str) - The JWT containing user_id and session_id of the user that is to leave the channel
        channel_id   (int) - The id of the channel that the user wants to join

    Exceptions:
        InputError - Occurs when the channel_id inputted does not belong to any channel that exists in the database
        AccessError - Occurs when 
                            1) the channel that the user is trying to join is private
                            2) The token inputted does not belong to any user

    Return Value:
        Returns an empty list regardless of conditions :)
    '''

    # Find the channel in the database
    channelFound = False
    i = 0

    # Loop throug channel data base until channel is found
    while not channelFound:
        if i >= len(src.data.channels):
            # If channel doesn't exist in database, inputError
            raise InputError
        elif src.data.channels[i]['channel_id'] == channel_id:
            # If channel is found
            channelFound = True
        i += 1

    i -= 1      # Undo extra increment

    auth_user_id, _ = decode(token)

    # Time to find the user details
    userFound = False
    j = 0
    while not userFound:
        if j >= len(src.data.users):
            # If user doesn't exist in database, AccessError
            raise AccessError
        elif src.data.users[j]['u_id'] == auth_user_id:
            userFound = True
        j += 1

    j -= 1      # Undo extra increment
    
    if src.data.channels[i]['is_public'] == False and src.data.users[j]['permission_id'] != 1:
        # If channel is private, AccessError
        raise AccessError

    # Time to add the user into the channel
    src.data.channels[i]['all_members'].append(src.data.users[j]['u_id'])

    # Done, return empty list 
    return {
    }

def channel_addowner_v1(token, channel_id, u_id):
    '''
    channel_addowner_v1 adds user with the u_id parameter to the associated channel's owner members, granting them
    owner permissions
    
    Arguments:
        token (str) - JWT containing { u_id, session_id }
        channel_id (int) - The id of the desired channel.
        u_id (int) - The id of desired user we want to add to owners
    Exceptions:
        InputError - Occurs when the channel_id used as a parameter does not already exist in the channels list.
        InputError - Occurs when the user with associated u_id is already an owner of the channel
        AccessError - Occurs when the user calling the function is not an authorised user.
    
    Return Value:
        Empty Dictionary
    '''

    auth_user_id, _ = decode(token)
    
    passed = False
    for check in src.data.channels:
        if check['channel_id'] == channel_id:
            passed = True
    if not passed:
        raise InputError
        
    for chans in src.data.channels:
        if chans["channel_id"] == channel_id:
            alreadyOwner = False
            for users in chans["owner_members"]:
                if users == u_id:
                    alreadyOwner = True
            if alreadyOwner == True:
                raise InputError

    # Access error
    dreamsOwner = False
    userAuth = False
    for users in src.data.users:
        if users['u_id'] == auth_user_id:
            if users['permission_id'] == 1:
                dreamsOwner = True
    for chans in src.data.channels:
        if chans["channel_id"] == channel_id:
            for users in chans["owner_members"]:
                if users == auth_user_id:
                    userAuth = True
                    break
    
    if dreamsOwner == False and userAuth == False:
        raise AccessError
    
    # now searches for channel_id
    for chan in src.data.channels:
        if chan["channel_id"] == channel_id:
            # ensure no duplicates
            chan["all_members"].append(u_id) if u_id not in chan["all_members"] else None
            chan["owner_members"].append(u_id) if u_id not in chan["owner_members"] else None
    push_added_notifications(auth_user_id, u_id, channel_id,-1)

    return {
    }

def channel_removeowner_v1(token, channel_id, u_id):
    '''
    channel_removeowner_v1 removes user with the u_id parameter to the associated channel's owner members, revoking their
    owner permissions.
    
    Arguments:
        token (str) - JWT containing { u_id, session_id }
        channel_id (int) - The id of the desired channel.
        u_id (int) - The id of desired user we want to remove from the channel's owners.
    Exceptions:
        InputError - Occurs when the channel_id used as a parameter does not already exist in the channels list.
        InputError - Occurs when the user with associated u_id is not an owner of the channel
        AccessError - Occurs when the user calling the function is not an authorised user.
    
    Return Value:
        Empty Dictionary
    '''

    auth_user_id, _ = decode(token)
    
    passed = False
    for check in src.data.channels:
        if check['channel_id'] == channel_id:
            passed = True
            break
    if not passed:
        raise InputError
    for chans in src.data.channels:
        if chans["channel_id"] == channel_id:
            userisOwner = False
            for users in chans["owner_members"]:
                if users == u_id:
                    userisOwner = True
                    break
    if not userisOwner:
        raise InputError

    # Access error
    dreamsOwner = False
    for users in src.data.users:
        if users['u_id'] == auth_user_id:
            if users['permission_id'] == 1:
                dreamsOwner = True
    
    for chans in src.data.channels:
        if chans["channel_id"] == channel_id:
            userAuth = False
            for users in chans["owner_members"]:
                if users == auth_user_id:
                    userAuth = True

    if dreamsOwner == False and userAuth == False:
        raise AccessError

    for chan in src.data.channels:
        if chan["channel_id"] == channel_id:
            for users in chan["owner_members"]:
                if users == u_id:
                    chan["owner_members"].remove(users)


    return {
    }







