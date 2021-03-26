import pytest
from src.channels import channels_list_v2, channels_listall_v2, channels_create_v1
from src.error import AccessError, InputError
import src.auth, src.channel, src.other
import jwt

SECRET = 'MENG'

AuID    = 'auth_user_id'
uID     = 'u_id'
cID     = 'channel_id'
allMems = 'all_members'
cName   = 'name'
fName   = 'name_first'
lName   = 'name_last'
chans   = 'channels'

@pytest.fixture
def invalid_token():
    return jwt.encode({'session_id': -1, 'user_id': -1}, SECRET, algorithm='HS256')

def test_channels_access_error(invalid_token):
    with pytest.raises(AccessError):
        channels_list_v2(invalid_token)
        channels_listall_v2(invalid_token)

def test_channels_list_valid():
    #* User is part of no channels
    '''
    < Register 2 users >
    < One creates a channel >
    < Run function >
    '''
    #* User is part of some channels
    '''
    < Register 3 users >
    < 2 create a channel for themselves >
    < 3rd creates a channel and invites both >
    < Run function >
    '''
    #* User is in all channels
    '''
    < Register user >
    < Create a channel >
    < Run function >
    '''
    pass

def test_channels_listall_valid():
    #* Private and public channels are both shown
    '''
    < Register 2 users>
    < One creates a public and private channel>
    < Other calls function >
    '''
    #* Joining/leaving channels does not affect the output
    '''
    < Register 2 users >
    < One creates a channel >
    < Invite other user >
    < Call function >
    < User leaves >
    < Call function >
    '''
    #* Running the function for two different valid AuIDs shoud have the same result
    '''
    < Register 2 users >
    < One creates a channel >
    < Assert both function calls are equal >
    '''
    pass

def test_channels_create():
    #* Ensure database is empty
    #! Clearing data
    src.other.clear_v1()
    
    #* Setup users and create shorthand for strings for testing code
    userID1 = src.auth.auth_register_v1("ayelmao@gmail.com", "Bl00dO4th", "C", "L")
    userID2 = src.auth.auth_register_v1("lolrofl@gmail.com", "pr3ttynAme", "S", "S")

    #* Test 1: Newly created public channel by userID1 appears in both of his channel list
    firstChannel = channels_create_v1(userID1[AuID], 'Oogway', True)
    assert {cID: firstChannel[cID], cName: 'Oogway'} in channels_list_v1(userID1[AuID])[chans]
    assert {cID: firstChannel[cID], cName: 'Oogway'} in channels_listall_v1(userID1[AuID])[chans]

    #* Test 2: Make sure this channel doesn't appear in userID2's channel list, but does in listall
    assert {cID: firstChannel[cID], cName: 'Oogway'} not in channels_list_v1(userID2[AuID])[chans]
    assert {cID: firstChannel[cID], cName: 'Oogway'} in channels_listall_v1(userID2[AuID])[chans]

    #* Test 3: Newly created private channel by userID2 appears in his channel list
    secondChannel = channels_create_v1(userID2[AuID], 'Yayot', False)
    assert {cID: secondChannel[cID], cName: 'Yayot'} in channels_list_v1(userID2[AuID])[chans]
    assert {cID: secondChannel[cID], cName: 'Yayot'} in channels_listall_v1(userID2[AuID])[chans]

    #* Test 4: Make sure this channel doesn't appear in of userID1's channel lists
    assert {cID: secondChannel[cID], cName: 'Yayot'} not in channels_list_v1(userID1[AuID])[chans]
    assert {cID: secondChannel[cID], cName: 'Yayot'} in channels_listall_v1(userID1[AuID])[chans]

    #* Test 5: InputError is raised when the channel name is more than 20 chars
    with pytest.raises(InputError):
        channels_create_v1(userID1[AuID], 'abcdefghijklmnopqrstuvwxyz', True)

    #* Finished testing for this function
    #! Clearing data
    src.other.clear_v1()