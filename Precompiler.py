
import json
import numpy
import sys
import Dijkstra
import FileIO
import test
import Visualizer
degree_sign= u'\N{DEGREE SIGN}'

class LatLong(object):
    '''
    Description
    ---------------------------------------------------------------------------
    Represents a Latitude and Longitudinal coordinates in
    decimal degrees. Takes decimal degree latitude and longitudinal
    values and separates into constituent parts (degrees, minutes and seconds)

    Class Variables
    ---------------------------------------------------------------------------
    dLat [number] : Degrees Latitude
    mLat [number] : Minutes Latitude
    sLat [number] : Seconds Latitude
    dLong [number] : Degrees Longitude
    mLong [number] : Minutes Longitude
    sLong [number] : Seconds Longitude
    srcLat [number] : The raw float decimal number latitude
    srcLong [number] : The raw float decimal number longitude

    Usage
    ---------------------------------------------------------------------------
    >>> latLong1 = LatLong(-75.651190010722587,43.800854964303937)
    >>> print(latLong)
    -76.0° 20.0' 55.715961398686886", 43.0° 48.0' 3.07787149417436"
    
    '''
    def __init__(self,decimalDegreesLat,decimalDegreesLong):
        '''
        Constructs a new LatLong Object.

        decimalDegreesLat: Raw decimal value of latitude (ex.-75.651190010722587 )        
        decimalDegreesLong: Raw decimal value of longitude (ex. 43.800854964303937 )
        
        '''
        self.dLat = numpy.floor(decimalDegreesLat)
        self.mLat = numpy.floor(60 * numpy.abs(decimalDegreesLat - self.dLat))
        self.sLat = 3600 * numpy.abs(decimalDegreesLat - self.dLat) - 60 * self.mLat
        
        self.dLong = numpy.floor(decimalDegreesLong)
        self.mLong = numpy.floor(60 * numpy.abs(decimalDegreesLong - self.dLong))
        self.sLong = 3600 * numpy.abs(decimalDegreesLong - self.dLong) - 60 * self.mLong
        self.srcLat = decimalDegreesLat
        self.srcLong = decimalDegreesLong
    def __str__(self):
        ''' 
        Returns a string representation of the LatLong object.
        '''
        return "{0}{1} {2}\' {3}\", {4}{5} {6}\' {7}\"".format(
            self.dLat,degree_sign,self.mLat,self.sLat,
            self.dLong,degree_sign,self.mLong,self.sLong
        )
    def __eq__(self,other):
        '''
        Returns True if both objects are equal. False otherwise.
        other[LatLong]: The other LatLong object to compare self to.
        Raises RuntimeError if 'other' is not of type LatLong
        '''
        if isinstance(other,LatLong):
            return self.srcLat == other.srcLat and self.srcLong == other.srcLong
        else:
            raise RuntimeError("LatLong.__eq__ failed! Argument of invalid type")
    __repr__ = __str__


class SiteID(object):
    '''
    Description
    ---------------------------------------------------------------------------
    Represents a USGS groundwater site identifcation number (8 to 10 digits long)
    There are two to three components for every SiteID:
    (watershed) | (value) | (extension)
        0001        9999    ---
        1001        9876    12
    Watersheds may range from 0000 to 9999; Values may range from 0000 to 9999
    Extensions may be None, 00 to 99. 

    Class Variables
    ---------------------------------------------------------------------------
    fullID [number] : Raw number in integer form
    watershed [number]: Watershed component
    value [number] : Value component
    extension [number]: Extension component (default= None)

    Usage
    ---------------------------------------------------------------------------
    >>> siteIDObj = SiteID(1001,9987)
    >>> siteIDObj2 = SiteID(1001,9987,13)
    >>> print(siteIDObj)
    >>> print(siteIDObj < siteIDObj2)
    10019987
    True
    '''
    def __init__(self,watershed = 1,value = 9999,extension = None):
        '''
        Constructs a new SiteID object

        watershed [number]: Watershed (0 to 9999)
        value [number]: 'value' portion (0 to 9999)
        extension [number]: Extension portion (0 to 99) (default=None)
        '''
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
        '''
        Returns a string version of the SiteID. Preserves all digits!
        i.e. A SiteID of 00454950 will NOT become "4595"
        Returns [str]
        '''
        if self.extension is None:
            return str("%08d"%self.fullID)
        else:
            return str("%10d"%self.fullID)
    def __lt__(self,other):
        '''
        Performs a '<' comparison between the calling SiteID and other

        other [number or SiteID]: The other side of the '<' to compare to

        Returns [bool]: True if self is less than other. False otherwise.
        '''
        if isinstance(other,int):
            return self.fullID < other
        elif isinstance(other,SiteID):
            if self.watershed == other.watershed:
                if self.value == other.value:
                    if self.extension is None and other.extension is None:
                        return False
                    else:
                        if self.extension is None:
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
        '''
        Performs a '<=' comparison between the calling SiteID and other

        other [number or SiteID]: The other side of the '<=' to compare to

        Returns [bool]: True if self is less than or equal to other. False otherwise.
        '''
        return self < other or self.__eq__(other)
    def __ge__(self,other):
        '''
        Performs a '>=' comparison between the calling SiteID and other

        other [number or SiteID]: The other side of the '>=' to compare to

        Returns [bool]: True if self is greater than or equal to other. False otherwise.
        '''
        return self > other or self.__eq__(other)
    def __gt__(self,other):
        '''
        Performs a '>' comparison between the calling SiteID and other

        other [number or SiteID]: The other side of the '>' to compare to

        Returns [bool]: True if self is greater than to other. False otherwise.
        '''
        return not self <= other
    def __eq__(self,other):
        '''
        Performs a '==' comparison between the calling SiteID and other

        other [number or SiteID]: The other side of the '==' to compare to

        Returns [bool]: True if self is equal to other. False otherwise.
        '''
        if isinstance(other,int):
            return self.fullID == other
        else:
            return self.fullID == other.fullID
    __repr__ = __str__


class Site(object):
    '''
    Description
    ---------------------------------------------------------------------------
    Represents the endpoint of a Flow. The "Nodes" of a Network. Stored
    in the SitesTable of the Network. Multiple sites may exist on the same point
    but all should have a unique ID

    Class Variables
    ---------------------------------------------------------------------------
    id [number] : Site's ID
    latlong [LatLong] : The location of the Site 
    z [number] : Unused
    h [number] : Unused
    flowsCon [list] : List of flows connected to the Site
    assignedID [number] : Assigned Site ID
    pendingUpstream : Number of flows that have yet to be processed, -1 if none
    downwardRefID [number] : Downward reference ID for the Site, None if there isn't any

    Usage
    ---------------------------------------------------------------------------

    '''
    def __init__(self,id,lat,long,h,z=0,flC = None):
        '''
        Constructs a new Site object

        id [number]: id (0 to 9999)
        lat [float] : Valid latitude for the Site
        long [float] : Valid longitude for the Site
        h [number] : Unused
        z [number] : Unused (default = 0)
        flC [list] : List will hold the flows connected to the Site (default = None)
        '''
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
        '''
        Performs a '==' comparison between the calling Site and other

        other [Site]: The other side of the '==' to compare to

        Returns [bool]: True if self is equal to other. False otherwise.
        '''
        return self.id == other.id
    def __lt__(self,other):
        '''
        Performs a '<' comparison between the calling Site and other

        other [Site]: The other side of the '<' to compare to

        Returns [bool]: True if self is less than or equal to other. False otherwise.
        '''
        return self.id < other.id
    def __gt__(self,other):
        '''
        Performs a '>' comparison between the calling Site and other

        other [Site] : The other side of the '>' to compare to

        Returns [bool] : True if self is greater than to other. False otherwise.
        '''
        return self.id > other.id
    
    def calculatePendingUpstream(self):
        '''
        Calculates the number of pending upstreams a site has

        Updates class variable "pendingUpstream"
        '''
        cs = self.connectedSites()     
        cntr = 0   
        for e in cs:
            if e[1] == UPSTREAM_CON:
                cntr += 1
                
        self.pendingUpstream = cntr

    def hasAssignedIDEquality(self,other):
        '''
        Performs an ID comparison between the calling Site and other

        other [Site] : The other side of the '==' to compare to

        Returns [bool] : True if self.self.assignedID is the same as other.self.assignedID. False otherwise.
        '''
        return self.assignedID == other.assignedID
    def hasPositionalEquality(self,other):
        '''
        Performs an LatLong comparison between the calling Site and other

        other [Site] : The other side of the '==' to compare to

        Returns [bool] : True if self.latlong is the same as other.latlong. False otherwise.
        '''
        return self.latLong == other.latLong
    def __str__(self):
        '''
        Returns a string version of the Site
        Returns [str]
        '''
        return "Site <{0}> {1}".format(self.id,self.latLong)
    def addFlow(self,flow):
        '''
        Adds a flow to the list of flows the Site is connected to 

        flow [Flow] : The flow object that is to be added to self.flowsCon

        '''
        self.flowsCon.append(flow)
    def isProperNode(self):
        '''
        Performs a check on the Site. Ensures that it is a proper Site.

        A proper Site has at either 1 or 3 flows connected. 

        Returns [bool] : True if it's a proper Site. False otherwise. 
        '''
        # Return if there is either one line connected (source or sink) or is a confluence (three)
        # Will return false if this site is intermediately on a line
        return len(self.flowsCon) >= 1 and len(self.flowsCon) <= 3 and not len(self.flowsCon) == 2
    
    def removeInvolvedFlows(self,site):
        '''
        DO NOT USE OUTSIDE FO PRECONFIGURATION

        Used it RemoveUseless() function. Deletes the flows that were connected
        to removed Sites. 

        '''
        i = 0        
        while i in range(len(self.flowsCon)):
            f = self.flowsCon[i]
            if f.upstreamSite == site or f.downstreamSite == site:
                self.flowsCon.remove(f)
            else:
                i += 1 
    

    def connectedSites(self):
        '''
        Creates a list of connected sites and provides them with important information
        to reduce look up time.

        Adds connected Sites to the list in a tuple with format : (Site, "DOWNSTREAM_CON"/"UPSTREAM_CON", flow)

        Returns [List((Site, Dir, Flow))] : Returns the list of connected sites. 
        '''
        csl = []
        for f in self.flowsCon:
            us = f.upstreamSite
            ds = f.downstreamSite
            if us == self:
                csl.append((ds,DOWNSTREAM_CON,f))
            elif ds == self:
                csl.append((us,UPSTREAM_CON,f))
        return csl
    
    def getUpstream(self):
        '''
        Creates a list of all upstream Sites from one Site

        Returns [List(Site)] : list of all upstream Sites
        '''
        ups = []
        cs = self.connectedSites()
        for con in cs:
            if con[1] == UPSTREAM_CON:
                ups.append(con[0])
        return ups

    def getDownstream(self):
        '''
        Creates a list of all downstream Sites from one Site

        Returns [List(Site)] : list of all downstream Sites
        '''
        down = []
        cs = self.connectedSites()
        for con in cs:
            if con[1] == DOWNSTREAM_CON:
                down.append(con[0])
        return down
    __repr__ = __str__

DOWNSTREAM_CON = 1
UPSTREAM_CON = 2

class Flow(object):
    '''
    Description
    ---------------------------------------------------------------------------
    Represents a flowline which connects two sites (either fake or real)
    Has unique ID to be updated in precompilation; contains reach code
    and length attributes as well as reference to which sites are the
    endpoints (these should be found in the sitesTable of the Network() object)

    Class Variables
    ---------------------------------------------------------------------------
    upstreamSite [Site] : The upstream Site of the flow
    downstreamSite [Site] : The downstream Site of the flow
    id [number] : The flow's Id number
    reachCode [number] : The flow's reach code 
    name [String] : The GNIS Name of the flow 
    length [float] : The length of the flow segment
    thisAndUpstream [float]: The length of the current flow segment + the distance to the "sink" Site.
    unadressable [bool] : Bool that represents if a flow has no allocated address space and must be ignored

    Usage
    ---------------------------------------------------------------------------

    '''
    def __init__(self,id,startSite,endSite,length,reachCode = -1,name=None):
        '''
        Constructs a new Flow object

        id [number]: id (0 to 9999)
        startSite [Site]: The upstream site of the flow
        endSite [Site]: The downstream site of the flow
        length [number] : The length of the flow
        reachCode [number] : The reach code of the flow (default = -1)
        name [String] : The name of the flow (default = None)
        '''
        self.upstreamSite = startSite
        self.downstreamSite = endSite
        self.id  = id
        self.reachCode = reachCode
        self.name = name
        self.length = length
        self.thisAndUpstream = self.length # This and upstream length
        self.unadressable = False # If a flow leads to a site which has already been ID'd, it must be part of the closing flow of a loop
                                # It has no allocated address space and must be ignored
    def __lt__(self,other):
        '''
        Performs an Flow priority comparision between the calling Site and other

        other [Site] : The other flow that will be compared

        Returns [bool] : True if self has a lower priority than other. False otherwise.
        '''
        return self.hasHigherPriority(other)

    def hasHigherPriority(self,otherFlow):
        '''
        Determines which flow to go to first

        Return [bool] : True if self has a higher priority than other. False otherwise.
        '''

        # Returns true if this is
        if self.name is None:
            if otherFlow.name is None:
                # Compare based on .thisAndUpstream
                return self.thisAndUpstream < otherFlow.thisAndUpstream
            else:
                return False # Other has higher priority bc it is named
        else:
            if otherFlow.name is None:
                return True # Self is named and other is not
            else:
                # Both are named, go by distance
                return self.thisAndUpstream < otherFlow.thisAndUpstream

    def __le__(self,other):
        '''
        Performs an Flow priority comparision between the calling Site and other

        other [Site] : The other flow that will be compared

        Returns [bool] : True if self has a lower priority than other or if they're equal to eachother. False otherwise.
        '''
        return self.hasHigherPriority(other) or self.__eq__(other)

    def __gt__(self,other):
        '''
        Performs an Flow priority comparision between the calling Site and other

        other [Site] : The other flow that will be compared

        Returns [bool] : True if self has a higher priority than other. False otherwise.
        '''
        return not self.__le__(other) 
    def __eq__(self,other):
        '''
        Compares this flow to 'other' Flow

        Returns [bool]: True if both Flow's reach codes are the same or have the same ID
        Precondition: 'other' must be a Flow object
        '''
        return self.reachCode == other.reachCode or self.id == other.id
    def __str__(self):
        '''
        Returns a string representation of the Flow, following this format:
        Flow <flow #> upstream is {upstreamSite.id}, downstream is {downstreamSite.id}
        (Note: upstreamSite.id refers to the associative number (0,1,2,3), NOT the SiteID's (10019999,...))

        Returns [string]: String representation
        '''
        return "Flow <{0}> upstream is {1}, downstream is {2}".format(self.id,self.upstreamSite.id,self.downstreamSite.id)
    __repr__ = __str__


class Network(object):
    '''
    Description
    ---------------------------------------------------------------------------
    Represents a collection of flows connected at the ends by sites and the relationships between each.
    Organized into two main tables a flow table and a site table (a table here is just a list).
    Keeps track of its total size (length of all flows combined)

    Class Variables
    ---------------------------------------------------------------------------
    totalSize [number]: Total length of the Network (length of all Flows). Must be 
                        Recomputed to be acurate via recalculateTotalLength()
    flowTable [List(Of Flow)]: The flows (or connections) in the Network
    siteTable [List(Of Site)]: The sites (or nodes) in the Network
    unitLength [number]: (IN KM!) How much distance before incrementing what
                         SiteID value portion should be assigned

    Usage
    ---------------------------------------------------------------------------
    (Here is an example of how to run the entire thing with a Network)
    >>> dictt = importJSON("Data/SmallNet001.json")
    >>> net = isolateNet(dictt,True)       
    >>> sinks = calculateSink(net)
    >>> setupSiteSafety(net)
    >>> faucets = calculateFaucets(net)
    >>> calculateUpstreamDistances(net,faucets)
    >>> net.recalculateTotalLength()
    >>> pSNA(net,SiteID(1001,9999,None),sinks[0])
    '''
    def __init__(self,flows,sites,unitLen = 1):
        '''
        Constructs a new Network object

        flows [List(Of Flow)]: Flowtable to initialize with
        sites [List (Of Site)]: Sitetable to initialize with
        unitLen [number]: How many (KM) before decrementing/incrementing the value portion of a SiteID
        '''
        self.totalSize = 0
        self.flowTable = flows
        self.siteTable = sites
        self.unitLength = unitLen # km; How many km before incrementing what ID should be assigned proportionally

    def recalculateTotalLength(self):
        '''
        Recalculates the Network's totalSize
        Returns [None]
        '''
        self.totalSize = 0
        for f in self.flowTable:
            self.totalSize += f.length
        
    def removeInvolvedFlows(self,site):
        '''
        Removes any flows from the flow table which have 'site' as
        one of the endpoints

        site [Site]: Site that if appearing in
                     a flow in the flow table, means the flow should be purged

        Returns [None]
        '''
        i = 0        
        while i in range(len(self.flowTable)):
            f = self.flowTable[i]
            if f.upstreamSite == site or f.downstreamSite == site:
                self.flowTable.remove(f)
            else:
                i += 1
        

def importJSON(filepath):
    '''
    Will import a dictionary from a JSON file

    filepath [string]: Filepath of the JSON file to import

    Returns [Dictionary(Formatted geoJSON dictionary)]: A formatted geoJSON dictionary in python!
    '''
    try:
        f = open(filepath,"r").read()
        y = json.loads(f)
        return y
    except IOError as e:
        print(e)
        return None

# Will return the site which either has positional eq with "site" or site itself
def peq(siteList,site):
    '''
    Will returns the site that has positional equality with 'site' argument or
    the provided 'site' variable itself.

    siteList [List(Of Site)]: List of sites to compare site with
    site [Site]: Site to compare with

    Returns [Site]: The site that has positional equality with 'site' argument or
    the provided 'site' variable itself.
    '''
    for e in siteList:
        if e.hasPositionalEquality(site):
            return e
    return site


def isolateNet(jsonDict,checkName=False):
    '''
    Isolate a network from a geoJSON dictionary (Give the fields we want and put into a class).
    Will consolodate the network upon creation to save time

    jsonDic [Dictionary]: The Dictionary provided from importing a json file
    checkName: [bool]: Should we include name fields in our network for flows/sites

    Returns [Network] An isolated network from JSON dictionary.
    '''

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

        if checkName:
            name = str(geomObj['properties']['GNIS_Name'])
            # If name is blank
            if len(name.strip()) == 0:
                name = None
        else:
            name = None

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
                
                fl2Add = Flow(theID,upGood,downGood,length,rc,name)    
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

            
            fl2Add = Flow(theID,upGood,downGood,length,rc,name)    
            upGood.addFlow(fl2Add)
            downGood.addFlow(fl2Add)            
            linesList.append(fl2Add)
        else:
            print("ERROR: Unknown object type encountered")
            raise RuntimeError()     
        
    
    return Network(linesList,sitesList)


def calculateSink(net):
    '''
    Calculate the sink for a given network. The sink is the most downstream
    Site of the entire Network. (If you think of the Network like a tree, it would
    be the root!)

    net [Network]: Network to perform analysis on

    Returns [Site]: The sink site of a network
    Raises RuntimeError if the graph has no sink (is invalid)!
    '''
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

def calculateFaucets(net):    
    '''
    Calculate the faucets for a given network. The 'faucets' are the sources of
    the water network. (If you think of the network as a tree, these would be the outermost
    leaf nodes)

    net [Network]: Network to perform analysis on.
    
    Returns List(Of Site): List of sites at the upstream-most areas of a network (faucets).
    '''
    faucets = []
    for s in net.siteTable:
        if len(s.flowsCon) == 1 and s.flowsCon[0].upstreamSite == s:
            # s is a faucet (the most upstream on a particular branch)
            faucets.append(s)
    return faucets


def setupSiteSafety(net):
    '''
    Will calculate the pending upstream number for every site in the sitetable

    net [Network]: The network to lookup sites in site-table.

    Returns [None]
    
    Notes: Do NOT call this method outside of preconfigured use. It will mess up the
    algorithm.
    '''
    for s in net.siteTable:
        s.calculatePendingUpstream()



def calculateUpstreamDistances(net,faucets):
    '''
    Recalculates the upstream distances for each Site in a Network starting from each faucet 
    (furthest sites from the sink, dendrites)
    

    net [Network]: Network to perform operations on.
    faucets [List(Of Site)]: A premade list of faucets used to complete method
    
    Returns [None]
    Raises RuntimeError if there is a multiple sink situation
    '''
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
    '''
    Determines all sites with positional equality

    net [Network]: Network whose sites we will compare locations

    Returns [List(Of Site)]: List of sites with positional equality
    '''
    l = []
    for site in net.siteTable:
        for situ in net.siteTable:
            if site == situ:
                continue
            elif site.hasPositionalEquality(situ):
                l.append((site,situ))
    return l


def removeUseless(net):
    ''' 
    Will remove sites from the network with only two neighbors (1 up 1 down)
    Will then merge the two flows together into one flow, keeping the length
    of 1 of the deleted flows. (This is done to resolve MultiLineString) entries in
    geoJSON files.

    net [Network]: Network to operate on

    Returns [None]
    Notes: Do NOT run this method if you want to take loops into account as this
    method will break the runtime if loops are present!
    '''
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




def pSNA(net,maxDownstreamID,sinkSite = None):
    '''
    Will assign real ID's to the fake nodes via the Proportional Site Naming Algorithm
    1km is the mininum distance to generate unique 8 digit ID's. The network must represent the 
    same watershed in this case.
    pSNA will NOT shift down ID's if one exists already. This is a theoretical model
    pSNA WILL generate 10 digit ID's if the distance accumulated between two sites is less than the
    unit length (1km by default)
    0000 | 0000
    WTRSHD  UNIQUE

    net [Network]: Network to perform algorithm on.
    maxDownstreamID [SiteID]: The maximal ID for the network. (This is what the sinksite will be)
    sinkSite [Site]: [Optional!] The lowermost site in the network. Parent to all. If not provided, will be computed 

    '''
    def alg(idBefore,totalAccum,leng,unitDist): 
        ''' 
        Internal core algorithm. 
        idBefore [SiteID]: What the ID was before
        totalAccum [number]: Total accumulated distance so far
        leng [number]: Length to be computed with
        unitDist [number]: How long before the value portion of an ID ticks down to -1
                            of the previous
        '''       
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
        if u.assignedID >= 0:
            # ID has already been assigned, must mean we just need to grab 
            # reference ID for this node
            u.downwardRefID = getLowestUpstreamNumber(net,u)
            continue

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
            elif theCon[1] == UPSTREAM_CON:
                # This has been assigned already, seems like we are on a loop
                theCon[2].unadressable = True # Designate that this should not be allowed for use
                print("Found Unadressable Flow sector: {0}".format(theCon[2]))
        lifechoices.sort(key= lambda conTup1: conTup1[2],reverse=False)
        # Add these future explorations into the queue in order
        if len(cs) > 1:
            # Confluence, append to the begining of queue
            # but preserve the order of lifechoices in the queue as well        
            # Standard procedure
            iIns = 0
            for conTup in lifechoices:
                queue.insert(iIns,conTup)
                iIns += 1
            refIDTup = (u,None,None)
            if len(cs) > 2:
                # 3 way branch; needs reference ID
                queue.insert(iIns,refIDTup)
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


def navigateToNearestConfluence(net,site):
    '''
    Will navigate to the nearest confluence. Returns the last flow which allowed reaching the
    confluence. 

    net [Network]: Network to perform analysis on
    site [Site]: Site to start operation from.

    Returns [Site]: Nearest confluence to argument 'site'
    Raises RuntimeWarning if 'site' is not in sitetable
    '''
    if not site in net.siteTable:
        raise RuntimeWarning("WARNING navigate_nearestConfluence() failed; site not in siteTable")
    s = site
    startSite = site
    flag = True
    rtrnFlow = None
    while flag:
        cs = s.connectedSites()
        dsCons = []
        for conTup in cs:
            if conTup[1] == DOWNSTREAM_CON:
                dsCons.append(conTup)
        if len(dsCons) != 1 or (len(cs) == 3 and  not s == startSite):
            # We are at the confluence or have reached the end.
            return rtrnFlow
        else:
            # Keep progressing
            rtrnFlow = dsCons[0][2]
            s = dsCons[0][0]


def navigateFurthestUpstream(net,site):
    '''
    Will navigate through the network to find the node at the end of a branch
    by using > operations.

    net [Network]: Network to perform analysis on.
    site [Site]: Site to start operation from.
    
    Returns [Site]: Furthest upstream site.
    '''
    sInvest = site
    flag = True
    while flag:
        cs = sInvest.connectedSites()
        flup = None        
        for con in cs:
            # If the connection is upstream it is pursuable
            if con[1] == UPSTREAM_CON:                
                if flup is None:
                    flup = con[2]
                else:
                    if con[2] < flup:
                        flup = con[2]
        if flup is None:
            # We have reached the upmost area on the branch
            flag = False
            break
        sInvest = flup.upstreamSite
    return sInvest
        

def getLowestUpstreamNumber(net,site):
    '''
    Gets the least (in number terms) upstream ID from a particular
    site. (Useful for refernce ID'ing confluences)

    net [Network]: Network to use in acquisition
    site [Site]: Starting point of curiosity

    Returns [SiteID]: Furthest upstream's SiteID
    '''
    return navigateFurthestUpstream(net,site).assignedID

# -------------------------------------------------------
# MAIN                  MAIN                    MAIN
# -------------------------------------------------------

if __name__ == "__main__":
    dictt = importJSON("Data/SmallNet001.json")
    net = isolateNet(dictt,True)    
    #net.unitLength = 0.1 # km
    sinks = calculateSink(net)
    #removeUseless(net)
    assert(len(sinks) == 1)
    setupSiteSafety(net)
    faucets = calculateFaucets(net)
    calculateUpstreamDistances(net,faucets)
    net.recalculateTotalLength()
    
    pSNA(net,SiteID(1001,9999,None),sinks[0])
    tp = test.TestPrecompiler()
    tp.create_files(net)
    Visualizer.create_visuals("Hello")

