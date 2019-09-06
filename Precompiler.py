import json
import numpy
import sys
import Dijkstra

degree_sign= u'\N{DEGREE SIGN}'

'''
Stores a latitude and longitude; converter from decimal degrees to longhand notation
'''
class LatLong(object):
    def __init__(self,decimalDegreesLat,decimalDegreesLong):
        self.dLat = numpy.floor(decimalDegreesLat)
        self.mLat = numpy.floor(60 * numpy.abs(decimalDegreesLat - self.dLat))
        self.sLat = 3600 * numpy.abs(decimalDegreesLat - self.dLat) - 60 * self.mLat
        
        self.dLong = numpy.floor(decimalDegreesLong)
        self.mLong = numpy.floor(60 * numpy.abs(decimalDegreesLong - self.dLong))
        self.sLong = 3600 * numpy.abs(decimalDegreesLong - self.dLong) - 60 * self.mLong
        self.srcLat = decimalDegreesLat
        self.srcLong = decimalDegreesLong
    def __str__(self):
        return "{0}{1} {2}\' {3}\", {4}{5} {6}\' {7}\"".format(
            self.dLat,degree_sign,self.mLat,self.sLat,
            self.dLong,degree_sign,self.mLong,self.sLong
        )
    def __eq__(self,other):
        return self.srcLat == other.srcLat and self.srcLong == other.srcLong
    __repr__ = __str__

class SiteID(object):
    def __init__(self,watershed = 1,value = 9999,extension = None):
        frm = str("%04d"%watershed)
        frm2 = str("%04d"%value)
        if extension is None:
            # 8 digit general ID
            self.fullID = int(frm + frm2)
            
        else:
            # 10 digit special case
            frm3 = str("%02d"%extension)
            self.fullID = int(frm + frm2 + frm3)
        self.watershed = watershed
        self.value = value
        self.extension = extension
    def __str__(self):
        if self.extension is None:
            return str("%08d"%self.fullID)
        else:
            return str("%10d"%self.fullID)
    def __lt__(self,other):
        if isinstance(other,int):
            return self.fullID < other
        elif isinstance(other,SiteID):
            if self.watershed == other.watershed:
                if self.value == other.value:
                    if self.watershed is None and other.watershed is None:
                        return False
                    else:
                        if self.watershed is None:
                            return False
                        else:
                            return True
                else:
                    return self.value < other.value
            else:
                return self.watershed < other.watershed
        else:
            raise RuntimeError("ERROR: SiteID __lt__ secondary argument not compatible!")
    def __le__(self,other):
        return self < other or self.__eq__(other)
    def __ge__(self,other):
        return self > other or self.__eq__(other)
    def __gt__(self,other):
        return not self <= other
    def __eq__(self,other):
        if isinstance(other,int):
            return self.fullID == other
        else:
            return self.fullID == other.fullID
    __repr__ = __str__



'''
Represents the endpoint of a flow line. The "Nodes" of a Network. Stored
in the SitesTable of the Network. Multiple sites may exist on the same point
but all should have a unique ID
'''
class Site(object):
    def __init__(self,id,lat,long,h,z=0,flC = None):
        self.id = id
        self.latLong = LatLong(lat,long)
        self.z = z
        self.h = h
        if flC == None:
            self.flowsCon = []
        self.assignedID = -1 # This is what is assigned via algorithm
        self.pendingUpstream = -1
        self.downwardRefID = None # This is what is stored as reference to the next downstream ID
                                    # For resolving assignments in the Plotter
    def __eq__(self,other):
        return self.id == other.id
    def __lt__(self,other):
        return self.id < other.id
    def __gt__(self,other):
        return self.id > other.id
    
    def calculatePendingUpstream(self):
        cs = self.connectedSites()     
        cntr = 0   
        for e in cs:
            if e[1] == UPSTREAM_CON:
                cntr += 1
                
        self.pendingUpstream = cntr

    def hasAssignedIDEquality(self,other):
        return self.assignedID == other.assignedID
    def hasPositionalEquality(self,other):
        return self.latLong == other.latLong
    def __str__(self):
        return "Site <{0}> {1}".format(self.id,self.latLong)
    def addFlow(self,flow):
        self.flowsCon.append(flow)
    def isProperNode(self):
        # Return if there is either one line connected (source or sink) or is a confluence (three)
        # Will return false if this site is intermediately on a line
        return len(self.flowsCon) >= 1 and len(self.flowsCon) <= 3 and not len(self.flowsCon) == 2
    ''' Return list of connected sites either upstream or downstream
    e
    ''' 
    def removeInvolvedFlows(self,site):
        i = 0        
        while i in range(len(self.flowsCon)):
            f = self.flowsCon[i]
            if f.upstreamSite == site or f.downstreamSite == site:
                self.flowsCon.remove(f)
            else:
                i += 1 
    def connectedSites(self):
        csl = []
        for f in self.flowsCon:
            us = f.upstreamSite
            ds = f.downstreamSite
            if us == self:
                csl.append((ds,DOWNSTREAM_CON,f))
            elif ds == self:
                csl.append((us,UPSTREAM_CON,f))
        return csl
    
    __repr__ = __str__

DOWNSTREAM_CON = 1
UPSTREAM_CON = 2
'''
Represents a flowline which connects two sites (either fake or real)
Has unique ID to be updated in precompilation; contains reach code
and length attributes as well as reference to which sites are the
endpoints (these should be found in the sitesTable of the Network() object)
'''
class Flow(object):
    def __init__(self,id,startSite,endSite,length,reachCode = -1):
        self.upstreamSite = startSite
        self.downstreamSite = endSite
        self.id  = id
        self.reachCode = reachCode
        self.length = length
        self.thisAndUpstream = self.length # This and upstream length
    def __lt__(self,other):
        return self.length < other.length
    def __gt__(self,other):
        return self.length > other.length
    def __eq__(self,other):
        return self.reachCode == other.reachCode or self.id == other.id
    def __str__(self):
        return "Flow <{0}> upstream is {1}, downstream is {2}".format(self.id,self.upstreamSite.id,self.downstreamSite.id)
    __repr__ = __str__

'''
Represents a collection of flows connected at the ends by sites.
Keeps track of its total size (length of all flows combined)
'''
class Network(object):
    def __init__(self,flows,sites):
        self.totalSize = 0
        self.flowTable = flows
        self.siteTable = sites
        self.unitLength = 1 # km; How many km before incrementing what ID should be assigned proportionally
    def recalculateTotalLength(self):
        self.totalSize = 0
        for f in self.flowTable:
            self.totalSize += f.length
        
    def removeInvolvedFlows(self,site):
        i = 0        
        while i in range(len(self.flowTable)):
            f = self.flowTable[i]
            if f.upstreamSite == site or f.downstreamSite == site:
                self.flowTable.remove(f)
            else:
                i += 1
        
'''
Will import a dictionary from a JSON file
'''
def importJSON(filepath):
    try:
        f = open(filepath,"r").read()
        y = json.loads(f)
        return y
    except IOError as e:
        print(e)
        return None

# Will return the site which either has positional eq with "site" or site itself
def peq(siteList,site):
    for e in siteList:
        if e.hasPositionalEquality(site):
            return e
    return site

'''
Isolate a network from a geoJSON dictionary
(Give the fields we want and put into a class).
Will consolodate the network upon creation to save
time
'''
def isolateNet(jsonDict):
    fList = jsonDict["features"]
    linesList = []
    sitesList = []
    siteCounter = 0

    for geomObj in fList:
        coordList = geomObj['geometry']['coordinates']
        upPoint = coordList[0]
        downPoint = coordList[len(coordList) - 1]
        theID = geomObj['properties']['OBJECTID']
        rc = geomObj['properties']['ReachCode']
        length = geomObj['properties']['LengthKM']
        upSite = None
        downSite = None
        if geomObj['geometry']['type'] == "MultiLineString":
            # We have a buggy entry, take the first entry only
            for fi in range(len(coordList)):
                upSite = Site(siteCounter,coordList[fi][0][0],coordList[fi][0][1],coordList[fi][0][3])
                upGood = peq(sitesList,upSite)
                if upGood == upSite:
                    siteCounter += 1
                    sitesList.append(upSite)

                eI = len(coordList[fi]) - 1
                # Take the last entry of the last line segment
                downSite = Site(siteCounter,coordList[fi][eI][0],coordList[fi][eI][1],coordList[fi][eI][3])
                downGood = peq(sitesList,downSite)
                if downGood == downSite:
                    siteCounter += 1                
                    sitesList.append(downSite)

                fl2Add = Flow(theID,upGood,downGood,length,rc)    
                upGood.addFlow(fl2Add)
                downGood.addFlow(fl2Add)                
                linesList.append(fl2Add)

        elif geomObj['geometry']['type'] == "LineString":
            upSite = Site(siteCounter,upPoint[0],upPoint[1],upPoint[3])
            upGood = peq(sitesList,upSite)
            if upGood == upSite:
                siteCounter += 1
                sitesList.append(upSite)
            downSite = Site(siteCounter,downPoint[0],downPoint[1],downPoint[3])
            downGood = peq(sitesList,downSite)
            if downGood == downSite:
                siteCounter += 1                
                sitesList.append(downSite)

            
            fl2Add = Flow(theID,upGood,downGood,length,rc)    
            upGood.addFlow(fl2Add)
            downGood.addFlow(fl2Add)            
            linesList.append(fl2Add)
        else:
            print("ERROR: Unknown object type encountered")
            raise RuntimeError()     
        
    
    return Network(linesList,sitesList)

'''
Calculate the sink for a given network.
Returns the ID of that Site
'''
def calculateSink(net):
    kaboodle = []
    for kit in net.siteTable:
        if len(kit.flowsCon) == 1:
            fds = kit.flowsCon[0].downstreamSite
            if fds == kit:
                # This site is downstream and is the only downstream site left
                kaboodle.append(kit)
    if len(kaboodle) != 1:
        raise RuntimeError("ERROR: calculateSink: Detected invalid graph")
    return kaboodle

'''
Calculate the faucets for a given network
Returns the 
'''
def calculateFaucets(net):
    faucets = []
    for s in net.siteTable:
        if len(s.flowsCon) == 1 and s.flowsCon[0].upstreamSite == s:
            # s is a faucet (the most upstream on a particular branch)
            faucets.append(s)
    return faucets

def setupSiteSafety(net):
    for s in net.siteTable:
        s.calculatePendingUpstream()


'''
Recalculates the upstream distances for a network starting from a sink
'''
def calculateUpstreamDistances(net,faucets):
    # Written by Nicole and Marcus
    queue = list(faucets)
    while len(queue) >= 1:
        u = queue.pop(0)
        cs = u.connectedSites()
        cntr = 0
        for con in cs:
            if con[1] == UPSTREAM_CON:
                cntr += 1
                if con[0].pendingUpstream == 0:
                    cntr -= 1
        u.pendingUpstream = cntr

        if u.id == 32:
            print("hey")
        if u.pendingUpstream > 0:
            # This site is not ready for assignment
            # Re-add it to the queue at the end
            queue.append(u)
            continue

        totalUp = 0
        totalDown = 0
        
        dcon = None
        if len(cs) == 1:
            # This is a true faucet
            
            if cs[0][1] == DOWNSTREAM_CON:
                dcon = cs[0][2]
                
            else:

                break # This is the sink
            # Append downstream site if not already in the queue
            if cs[0][0] not in queue:
                queue.append(cs[0][0])
        else:
            
            for entry in cs:
                if entry[1] == DOWNSTREAM_CON:
                    if dcon is None:
                        # add to totalDown
                        totalDown += entry[2].length
                        dcon = entry[2]
                        # Append downstream site if not already in the queue
                        if entry[0] not in queue:
                            queue.append(entry[0])
                else:
                   
                    totalUp += entry[2].thisAndUpstream
            totalDown += totalUp
            if dcon is None:
                # Reached the end
                raise RuntimeError("ERROR: calculateUpstreamDistances() invalid end")
            else:
                dcon.thisAndUpstream = totalDown

    

def positionalEqualityList(net):
    l = []
    for site in net.siteTable:
        for situ in net.siteTable:
            if site == situ:
                continue
            elif site.hasPositionalEquality(situ):
                l.append((site,situ))
    return l

''' Merged flows inherit the length of the subsegments
They do NOT add these lengths together
'''
def removeUseless(net):
    i = 0
    while i in range(len(net.siteTable)):
        sit = net.siteTable[i]
        cs = sit.connectedSites()
        if len(cs) == 2:
            # This site is deletable
            coni0 = cs[0]
            coni1 = cs[1]
            assert(coni0[2].length == coni1[2].length)
            newLen = coni0[2].length
            fl2Add = None
            if coni0[1] == DOWNSTREAM_CON:
                # coni0 is downstream of deletable site ('sit')
                # coni1 is upstream
                fl2Add = Flow(coni0[2].id,coni1[0],coni0[0],newLen,coni0[2].reachCode)  
            else:
                # coni0 is upstream of 'sit'
                # coni1 is downstream
                fl2Add = Flow(coni1[2].id,coni0[0],coni1[0],newLen,coni1[2].reachCode) 
            net.removeInvolvedFlows(sit)
            coni0[0].removeInvolvedFlows(sit)
            coni1[0].removeInvolvedFlows(sit)
            
            net.siteTable.remove(sit)
            coni0[0].flowsCon.append(fl2Add)
            coni1[0].flowsCon.append(fl2Add)
            net.flowTable.append(fl2Add)
        else:
            i += 1



'''
Will assign real ID's to the fake nodes via the Proportional Site Naming Algorithm
1km is the mininum distance to generate unique 8 digit ID's. The network must represent the 
same watershed in this case.
pSNA will NOT shift down ID's if one exists already. This is a theoretical model
pSNA WILL generate 10 digit ID's if the distance accumulated between two sites is less than the
unit length (1km by default)
0000 | 0000
WTRSHD  UNIQUE
'''
def pSNA(net,maxDownstreamID,sinkSite = None):
    def alg(idBefore,totalAccum,leng,unitDist):
        
        frac = leng / unitDist        
        newValue = int(idBefore.value - numpy.floor(frac))
        
        if newValue == idBefore.value:
            # Alter the extension
            
            unitExt = unitDist / 100
            newExt = int(numpy.floor(leng / unitExt))
            if not idBefore.extension is None:            
                newExt += idBefore.extension
            if newExt >= 99:
                # You should have decremented the value, mathematically
                newValue -= 1
                return SiteID(idBefore.watershed,newValue)
            if newExt == idBefore.extension:                
                # Add one to the previous extension and try
                return SiteID(idBefore.watershed,newValue,idBefore.extension + 1)             
            else:
                return SiteID(idBefore.watershed,newValue,newExt)
        else:
            return SiteID(idBefore.watershed,newValue)
    #---------------------------------------------------------------------

    # Use bitwise or to format final values
    if sinkSite is None:
        sinkSite = calculateSink(net)
    queue = []  
    starterTuple = (sinkSite,None,None)  
    queue.append(starterTuple)
    # Step 1: Starting from the sink site, assign the site.assignedID field
    idNext = maxDownstreamID
    distAccum = 0
    while len(queue) >= 1:
        # Pop out the tuple
        t = queue.pop(0)
        u = t[0]
        

        if t[2] is None:
            # Assume we are at start
            distAccum += 0
        else:
            distAccum += t[2].length
        cs = u.connectedSites()
        lifechoices = [] # The upstream paths we may choose              
        for theCon in cs:
            if theCon[1] == UPSTREAM_CON and theCon[0].assignedID < 0:
                # The connection is upstream and has not been assigned yet
                lifechoices.append(theCon)
                
        lifechoices.sort(key= lambda conTup1: conTup1[2].thisAndUpstream,reverse=False)
        # Add these future explorations into the queue in order
        if len(cs) > 1:
            # Confluence, append to the begining of queue
            # but preserve the order of lifechoices in the queue as well
            iIns = 0
            for conTup in lifechoices:
                queue.insert(iIns,conTup)
                iIns += 1
        elif len(cs) == 1:
            # Non-Confluence, append to the end of the queue
            # This is to handle special cases such as loops
            if cs[0][0].assignedID < 0:
                # Not assgned yet!
                queue.append(cs[0])
        else:
            # INVALID NODE
            #raise RuntimeError("ERROR: pSNA() Did you run removeUseless() before?")
            pass
        if t[2] is None:
            u.assignedID = maxDownstreamID
            idNext = u.assignedID
        else:
            newID = alg(idNext,distAccum,t[2].length,net.unitLength)        
            u.assignedID = newID
            u.downstreamID = idNext # The previous downstream ID is this
            idNext = newID

'''
Will navigate to the nearest confluence. Returns the last flow which allowed reaching the
confluence. 
'''
def navigateToNearestConfluence(net,site):
    if not site in net.siteTable:
        raise RuntimeWarning("WARNING navigate_nearestConfluence() failed; site not in siteTable")
    s = site
    flag = True
    rtrnFlow = None
    while flag:
        cs = s.connectedSites()
        dsCons = []
        for conTup in cs:
            if conTup[1] == DOWNSTREAM_CON:
                dsCons.append(conTup)
        if len(dsCons) != 1 or len(cs) == 3:
            # We are at the confluence or have reached the end.
            return rtrnFlow
        else:
            # Keep progressing
            rtrnFlow = dsCons[0][2]
            s = dsCons[0][0]
    
''' Will go back and assign reference ID's for lowest downstream 
Pre-requisite: Run algorithm to asign ID's first
'''
def confluenceReferenceIDAssign(net,faucets = None):
    if faucets is None:
        faucets = calculateFaucets(net)
    for s in faucets:
        f = navigateToNearestConfluence(net,s)
        confluence = f.downstreamSite
        conCons = confluence.connectedSites()
        # Find the other upstream of the confluence
        otherUpstream = None
        for sc in conCons:
            if sc[1] == UPSTREAM_CON:
                if sc[2] != f:
                    otherUpstream = sc[2]
        
        # If there is none, we dont need to do reference ID assign
        if otherUpstream is None:
            continue # We dont have to assign a downwards opening confluence
        if confluence.downwardRefID is None:
            if f.thisAndUpstream < otherUpstream.thisAndUpstream:
                confluence.downwardRefID = s.assignedID
        else:
            # Reference ID was already assigned; there is an error
            continue
# -------------------------------------------------------
# MAIN                  MAIN                    MAIN
# -------------------------------------------------------

if __name__ == "__main__":
    dictt = importJSON("Data/SmallNet001.json")
    net = isolateNet(dictt)    
    #net.unitLength = 0.1 # km
    sinks = calculateSink(net)
    removeUseless(net)
    assert(len(sinks) == 1)
    setupSiteSafety(net)
    faucets = calculateFaucets(net)
    calculateUpstreamDistances(net,faucets)
    net.recalculateTotalLength()

    pSNA(net,SiteID(1001,9999,None),sinks[0])
    confluenceReferenceIDAssign(net,faucets)
    print(net)

