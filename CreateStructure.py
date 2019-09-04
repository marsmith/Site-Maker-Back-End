import json
import numpy
import sys

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
        self.mathID = -1
    def __eq__(self,other):
        return self.id == other.id
    def __lt__(self,other):
        return self.id < other.id
    def __gt__(self,other):
        return self.id > other.id
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

'''
Recalculates the upstream distances for a network starting from a sink
'''
def calculateUpstreamDistances(net,faucets):
    # Written by Nicole and Marcus
    queue = list(faucets)
    while len(queue) >= 1:
        u = queue.pop(0)
        totalUp = 0
        totalDown = 0
        cs = u.connectedSites()
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
Will assign real ID's to the fake nodes via the Simple Proportional Creation Algorithm
1km is the mininum distance to generate unique 8 digit ID's.
0000 | 0000
WTRSHD  UNIQUE
'''
def idByProportion(net,maxDownstreamID,watershed):
    pass

if __name__ == "__main__":
    dictt = importJSON("SmallNet001.json")
    net = isolateNet(dictt)    
    sinks = calculateSink(net)
    removeUseless(net)
    assert(len(sinks) == 1)
    faucets = calculateFaucets(net)
    calculateUpstreamDistances(net,faucets)
    net.recalculateTotalLength()
    idByProportion(net,9999,1001)
    print(net)

