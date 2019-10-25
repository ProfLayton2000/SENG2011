from classes import *

system = MainSystem()
currentUser = None
def login():
    userType = input("Login Type (DONOR|PATH_CENTRE|HOSPITAL|VAMPIRE): ").upper().replace(' ','_')
    loginID = input("Login ID: ")
    password = input("Password: ")
    userList = []
    if userType == "DONOR":
        userList = system.getDonors()
    elif userType == "PATH_CENTRE":
        userList = system.getPathCentres()
    elif userType == "HOSPITAL":
        userList = system.getHospitals()
    elif userType == "VAMPIRE":
        userList.append(system.getVampire())
    
    for user in userList:
        if user.id == loginID and user.getPassword() == password:
            global currentUser
            currentUser = user
            return True
    
    return False

def logout():
    print("Logging out...")
    global currentUser
    currentUser = None
    print("Logged out.")
    return True

def showHelp():
    global currentUser
    print("You can use commands:")
    print("QUIT - Quit")
    print("HELP - Show help")
    if (currentUser == None):
        print("LOGIN - Login")
        return

    if (currentUser.getType() == UserType.DONOR):
        print("You can't do sht yet")
        print("Have a nice day")
    elif (currentUser.getType() == UserType.PATH_CENTRE):
        print("ADD_DONOR - Add a new donor")
        print("ADD_BLOOD - Add a new packet of blood")
        print("CHECK_INVENTORY - Check the inventory")
        print("MARK_BLOOD - Mark blood as clean/unclean")
        print("SEND_BLOOD - Send a specific packet to vampire")
    elif (currentUser.getType() == UserType.HOSPITAL):
        print("CHECK_INVENTORY - Check the inventory")
        print("DISPOSE_BLOOD - Mark blood as unclean and dispose")
        print("REQUEST_BLOOD - Request packets of a specific blood type")
    elif (currentUser.getType() == UserType.VAMPIRE):
        print("CHECK_INVENTORY - Check the inventory")
        print("CHECK_LEVELS - Get a summary of the blood levels")
        print("CHECK_REQUESTS - List the incoming requests")
    print("LOGOUT - Logout")

def parseDate(dateStr):
    try:
        date = datetime.strptime(dateStr, '%d/%m/%Y')
        time = round(date.timestamp())
        return time
    except:
        return None

def showStatus():
    global currentUser
    if (currentUser == None):
        print("Not logged in")
    else:
        print("Name: ",currentUser.getName())
        print("Type: ",currentUser.getTypeName())

def normalCommand(cmd):
    global currentUser
    if (cmd == "LOGIN"):
        if (login()):
            print("Log in succeeded, hello",currentUser.getName())
            print("Type LOGOUT to logout")
        else:
            print("Log in failed")
        return True
    return False

def donorCommand(cmd):
    return True

def processCommand(cmd):
    global currentUser
    if (cmd == "HELP"):
        showHelp()
        return True
    else:
        if (currentUser == None):
            return normalCommand(cmd)
        else:
            type = currentUser.getType()
            if (cmd == "LOGOUT"):
                return logout()
            elif (type == UserType.DONOR):
                return donorCommand(cmd)
            elif (type == UserType.PATH_CENTRE):
                return pathCentreCommand(cmd)
            elif (type == UserType.VAMPIRE):
                return vampireCommand(cmd)
            elif (type == UserType.HOSPITAL):
                return hospitalCommand(cmd)
            
        return False

def addDonor():
    givenName = input("Given Name: ")
    familyName = input("Family Name: ")
    email = input("Email: ")

    newID = system.addDonor(givenName,familyName,email)

    print("New ID:",newID,", Password: password")
    return True

def parseBlood():
    bloodType = input("Blood type (O_NEG,O_POS,etc.): ").upper().replace(' ','_')
    if bloodType not in BloodType.__members__ and bloodType != "CANCEL":
        print("Invalid blood type. Type CANCEL to cancel")
        bloodType = input("Blood type (O_NEG,O_POS,etc.): ").upper().replace(' ','_')
    if bloodType == "CANCEL":
        return None
    else:
        return bloodType

def addBlood():
    bloodType = parseBlood()
    if (bloodType == None):
        print("Cancelling submission")
        return True
    dateStr = input("Donation date (DD/MM/YYYY): ")
    donateDate = parseDate(dateStr)
    if donateDate == None:
        print("Bad date format, cancelling submission")
        return True
    donateLoc = input("Donation location: ")
    donorID = input("Donor ID: ")

    if (system.addPacket(currentUser,bloodType,donateDate,donateLoc,donorID)):
        print("Packet added!")
    else:
        print("Bad request")
    return True

def markBlood():
    packetID = input("Packet ID: ")
    newStatus = input("New status (CLEAN/UNCLEAN): ").upper().replace(' ','_')
    if (newStatus != "CLEAN" and newStatus != "UNCLEAN" and newStatus != "QUIT"):
        print("Not a valid status. Type CANCEL to cancel.")
        newStatus = input("New status (CLEAN/UNCLEAN): ").upper().replace(' ','_')
    if (newStatus == "CANCEL"):
        print("Cancelling changes....")
        return True
    # if not ():
    if not (system.markPacket(currentUser,packetID,newStatus)):
        print("Packet",packetID,"not found")
        return True
    print("Status of",packetID,"set to",newStatus)
    if (newStatus == "CLEAN"):
        print("Sending off to vampire...")
        sendBlood(packetID)
    return True

def disposeBlood(pID=None):
    packetID = pID
    if (packetID == None):
        packetID = input("Packet ID: ")
    if (system.disposePacket(currentUser,packetID)):
        print("Disposed packet",packetID)
    else:
        print("Packet",packetID,"not found")
    return True

def sendBlood(pID=None):
    packetID = pID
    if (packetID == None):
        packetID = input("Packet ID: ")

    addressID = 'vampire'
    if (currentUser.getType() != UserType.PATH_CENTRE):
        addressID = input("Hospital ID: ")

    if (system.sendPacketByID(currentUser,packetID,addressID)):
        print("Sent packet",packetID,"to",addressID)
    else:
        print("Bad request")
    return True

def requestBlood():
    # requestID,user.getID(),requestDate,type,nPackets,useBy
    bloodType = parseBlood()
    if (bloodType == None):
        print("Cancelling submission")
        return True
    nPackets = int(input("Number of packets: "))
    if (nPackets <= 0):
        print("Request must be a positive integer")
        return True
    dateStr = input("Use by (DD/MM/YYYY): ")
    useBy = parseDate(dateStr)
    if useBy == None:
        print("Bad date format, cancelling submission")
        return True
    now = round(datetime.timestamp(datetime.now()))
    if (useBy < now):
        print("Date in the past not allowed")
        return True
    if (system.makeRequest(currentUser,now,bloodType,nPackets,useBy)):
        print("Request got through")
    else:
        print("Request failed")
    return True

def pathCentreCommand(cmd):
    found = True
    if (cmd == "ADD_DONOR"):
        addDonor()
    elif (cmd == "ADD_BLOOD"):
        addBlood()
    elif (cmd == "CHECK_INVENTORY"):
        system.printInventory(currentUser)
    elif (cmd == "MARK_BLOOD"):
        markBlood()
    elif (cmd == "SEND_BLOOD"):
        sendBlood()
    else:
        found = False
    return found

def vampireCommand(cmd):
    found = True
    if (cmd == "CHECK_INVENTORY"):
        system.printInventory(currentUser)
    elif (cmd == "CHECK_LEVELS"):
        system.printLevels(currentUser)
    elif (cmd == "CHECK_REQUESTS"):
        system.showRequests(currentUser)
    else:
        found = False
    return found

def hospitalCommand(cmd):
    found = True
    if (cmd == "CHECK_INVENTORY"):
        system.printInventory(currentUser)
    elif (cmd == "DISPOSE_BLOOD"):
        disposeBlood()
    elif (cmd == "REQUEST_BLOOD"):
        requestBlood()
    else:
        found = False
    return found


on = True
print("Type 'QUIT' to quit, 'STATUS' for your current info, 'HELP' for available commands")
while on:
    cmd = input("$ ")
    tempCmd = cmd.upper()
    tempCmd = tempCmd.replace(' ','_')
    if (tempCmd == "QUIT"):
        print("Shutting down...")
        print("Shut down")
        on = False
    elif (tempCmd == "STATUS"):
        showStatus()
    else:
        if not (processCommand(tempCmd)):
            print("'"+cmd+"'",'is not a real command')
    print("----------------------------")
