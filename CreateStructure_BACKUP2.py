import json
import numpy

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
    def __init__(self,id,lat,long,h,z=0,flC = []):
        self.id = id
        self.latLong = LatLong(lat,long)
        self.z = z
        self.h = h
        self.flowsCon = flC
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
    __repr__ = __str__

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
    
'''
Will import a dictionary from a JSON file
'''
def importJSON(filepath):
    try:
        f = open(filepath,"r").read()
        y = json.loads(f)
        return y
    except e:
        print(e)
        return None

'''
Isolate a network from a geoJSON dictionary
(Give the fields we want and put into a class)
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
        
        upSite = Site(siteCounter,upPoint[0],upPoint[1],upPoint[3])
        sitesList.append(upSite)
        siteCounter += 1
        downSite = Site(siteCounter,downPoint[0],downPoint[1],downPoint[3])
        sitesList.append(downSite)  
        fl2Add = Flow(theID,upSite,downSite,length,rc)    
        upSite.addFlow(fl2Add)
        downSite.addFlow(fl2Add)
        siteCounter += 1
        linesList.append(fl2Add)
    
    return Network(linesList,sitesList)

'''
Remove all sites in network which are overlaping based on geometry
Update references to these sites in the flow table
'''
def consolodateNetwork(net):
    # Go through flows and see if endpoints of each flow are also endpoints of other flows
    for flow in net.flowTable:
        sLook = flow.downstreamSite
        for fl2 in net.flowTable:
            if flow == fl2:
                continue
            else:
                # Do comparison
                if fl2.downstreamSite.hasPositionalEquality(sLook):
                    # Make fl2's downstream point sLook
                    markedForDelete = fl2.downstreamSite
                    fl2.downstreamSite = sLook
                    net.siteTable.remove(markedForDelete)

'''
Calculate the sink for a given network. Returns the ID of that Site
'''
def calculateSink(net):
    kaboodle = []
    for kit in net.siteTable:
        if len(kit.flowsCon) == 1:
            fds = kit.flowsCon[0].downstreamSite
            if fds == kit:
                # This site is downstream and is the only downstream site left
                kaboodle.append(kit)
    return kaboodle

'''
Will assign real ID's to the fake nodes via the Simple Proportional Creation Algorithm
1km is the mininum distance to generate unique 8 digit ID's.
0000 | 0000
WTRSHD  UNIQUE
'''
def idByProportion(maxDownstreamID,watershed):
    pass

if __name__ == "__main__":
    dictt = importJSON("Converted.json")
    net = isolateNet(dictt)
    consolodateNetwork(net)
    sinks = calculateSink(net)
    print(net)

