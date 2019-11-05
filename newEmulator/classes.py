from enums import enum
from algos import objectBubbleSort,objectSortedInsert

class Vampire(object):
    def __init__(self):
        self._bloodTypeTable = {
            "O_NEG" : 0,
            "O_POS" : 1,
            "A_NEG" : 2,
            "A_POS" : 3,
            "B_NEG" : 4,
            "B_POS" : 5,
            "AB_NEG" : 6,
            "AB_POS" : 7
        }

        self._statusTable = {
            "UNCLEAN": 0,
            "CLEAN": 1
        }

        self._locationTable = {
            "DUMP": 0,
            "VAMPIRE": 1
        }

        self._inventory = Inventory(len(self._bloodTypeTable))

        self._donorDatabase = DonorDatabase()
        self._bloodDatabase = BloodDatabase()

        self._day = 0

#     method containsValue(m: map<int,char>, val: char) returns (b: bool) 
#     ensures b <==> exists i :: i in m && m[i] == val;
# {
#     return val in m.Values;
# }

    # Add a donor to the system
    def addDonor(self,firstName,lastName):
        self._donorDatabase.addDonor(firstName,lastName)

    def addLocation(self,loc):
        self._locationTable[loc] = len(self._locationTable)

    def printLocations(self):
        for key in self._locationTable:
            print(str(self._locationTable[key])+":",key)

    # Accept blood
    def makeDeposit(self,bloodTypeStr,expiryDate,donorID):
        if bloodTypeStr not in self._bloodTypeTable:
            return False
        bloodIndex = self._bloodTypeTable[bloodTypeStr]
        newPacket = self._bloodDatabase.addPacket(bloodIndex,expiryDate,donorID)
        self._inventory.addPacketID(newPacket)
        return True

    # Give blood
    def makeRequest(self,bloodTypeStr,nPackets,useBy,dest):
        if bloodTypeStr not in self._bloodTypeTable:
            return False
        if dest not in self._locationTable:
            self.addLocation(dest)
        destIndex = self._locationTable[dest]
        bloodIndex = self._bloodTypeTable[bloodTypeStr]
        accepted = self._inventory.doRequest(bloodIndex,nPackets,useBy,destIndex)
        return accepted

    # Increment the day and remove bad blood
    def cleanUp(self):
        self._day += 1
        self._inventory.cleanUp(self._day)

    # Debugging
    def printInventory(self,field):
        print("Current day:",self._day)
        self._inventory.printInventory(field)

    # Debugging
    def printDonors(self):
        self._donorDatabase.printDonors()

    # Debugging
    def printBlood(self,field):
        self._bloodDatabase.printBlood(field)

    # Search blood database
    def searchBlood(self,field,value):
        packets = self._bloodDatabase.searchBlood(field,value)
        for p in packets:
            p.toString()

class Inventory(object):
    def __init__(self,nBloodTypes):
        self._lowBloodLevels = [1] * nBloodTypes
        self._maxBloodLevels = [10] * nBloodTypes
        self._packets = []

    # Put a packet into the inventory
    def addPacketID(self,packetObj):
        objectSortedInsert(self._packets,"EXPIRY_DATE",packetObj)
        
    # Remove anything past expiry
    def cleanUp(self,currDay):
        trash = []
        for p in self._packets:
            if p.getField("EXPIRY_DATE") < currDay:
                trash.append(p)
        for p in trash:
            p.dump()
            self._packets.remove(p)

    # Debugging, print the inventory
    def printInventory(self,field):
        objectBubbleSort(self._packets,field)
        for p in self._packets:
            p.toString()
        objectBubbleSort(self._packets,"EXPIRY_DATE")

    # Do the request
    def doRequest(self,type,nPackets,useBy,dest):
        objectBubbleSort(self._packets,"EXPIRY_DATE")
        sendPackets = []
        i = 0
        while i < len(self._packets) and len(sendPackets) < nPackets:
            if (self._packets[i].getField("TYPE") == type and useBy <= self._packets[i].getField("EXPIRY_DATE")):
                sendPackets.append(self._packets[i])
            i += 1

        if len(sendPackets) < nPackets:
            return False

        for p in sendPackets:
            self._packets.remove(p)
            p.sendTo(dest)

        return True

class BloodDatabase(object):
    def __init__(self):
        self._entries = []
        self._sortedBy = "EXPIRY_DATE"

    def addPacket(self,bloodType,expiryDate,donorID):
        p = BloodPacket(bloodType,expiryDate,donorID)
        objectSortedInsert(self._entries,self._sortedBy,p)
        return p

    def printBlood(self,field):
        objectBubbleSort(self._entries,field)
        for p in self._entries:
            p.toString()
        objectBubbleSort(self._entries,self._sortedBy)

    def searchBlood(self,field,value):
        returnPackets = []
        for p in self._entries:
            if (p.getField(field) == value):
                returnPackets.append(p)
        return returnPackets

class BloodPacket(object):
    def __init__(self,bloodType,expiryDate,donorID):
        self._bloodType = bloodType
        self._expiryDate = expiryDate
        self._donorID = donorID
        self._status = 1
        self._currLoc = 1
    
    def toString(self):
        print("TYPE:",self._bloodType,"EXP DATE:",self._expiryDate,"DONOR:",self._donorID,"STATUS:",self._status,"LOC:",self._currLoc)

    def getField(self,field):
        if (field == "TYPE"):
            return self._bloodType
        elif (field == "EXPIRY_DATE"):
            return self._expiryDate
        elif (field == "DONOR_ID"):
            return self._donorID
        elif (field == "STATUS"):
            return self._status
        return -1

    def dump(self):
        self._status = 0
        self._currLoc = 0

    def sendTo(self,dest):
        self._currLoc = dest

class DonorDatabase(object):
    def __init__(self):
        self._entries = []
        self._sortedBy = "LAST_NAME"

    def addDonor(self,firstName,lastName):
        d = Donor(firstName,lastName,len(self._entries))
        objectSortedInsert(self._entries,self._sortedBy,d)

    def printDonors(self):
        for d in self._entries:
            d.toString()

class Donor(object):
    def __init__(self,firstName,lastName,id):
        self._id = id
        self._firstName = firstName
        self._lastName = lastName

    def toString(self):
        print(self._id,self._firstName,self._lastName)

    def getField(self,field):
        if (field == "FIRST_NAME"):
            return self._firstName
        elif (field == "LAST_NAME"):
            return self._lastName
        elif (field == "ID"):
            return self._id
        return -1