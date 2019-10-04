import shapefile
from Precompiler import *
import arcpy

def getPosHash(point,index= None):
    if index is None:

        return "{0},{1}".format(point[0],point[1])
    else:
        return "{0},{1}:{2}".format(point[0],point[1],index)

def importShapefile_TriDict(path):
    '''
    Imports a shapefile as a tuple of dictionaries. 
    path [string]: String of the shapefile .shp file and inside folder
    Returns [Tuple(startPointDict,endPointDict,reachCodeDict)]: Tuple of dictionaries; the first is startPoint location (upstream) hashed by location
                                                  The seconds is endPoint location (downstream) hashed by location
                                                  The third is hashed based on rechCode
            Since multiple lines may share the same point, it is also hashed by a counter at the end (":1",":2", etc...) up to 3
            There may be no more than three lines intersecting at a point. Otherwise there is a geological data error!
    '''
    def placeInDict(dict,point,shape,limit=4):
        '''
        Will place the point in a dictionary and link it to a shape. If
        there are multiple shared entries for the same coordinate, the endtag is incremented
        for hashing sake.

        dict [Dictionary(Of string,Shape)]: Dictionary to use for insertion
        point [Tuple (#x,#y)]: Tuple of the x,y coordinates
        shape [Shape]: A shape entry in a shapefile

        Returns [None]
        '''
        for i in range(0,limit):        
            hstr = getPosHash(point,i)
            if not hstr in dict.keys():
                # Safe to insert, it doesnt exist
                dict[hstr] = shape
                return
        raise RuntimeError("Error: Points already exist!")

    def retrieveShared(dict,point,limit=4):
        '''
        Will retrieve a list of all identical points (in terms of geographic coordinate).
        Since multiple points may exist on the same coordinate, an endtag is incremented to 
        retrieve the list

        dict [Dictionary(Of string,Shape)]: Dictionary to use for insertion
        point [Tuple (#x,#y)]: Tuple of the x,y coordinates

        Returns [List(Of ShapeRecord)]: List of shape-record which share the common end/startpoint as
        defined by 'point'
        '''
        l = []
        for i in range(limit):        
            hstr = getPosHash(point,i)
            try:
                l.append(dict[hstr])
            except Exception as p:
                return l
        return l

    # Stage 1: Read in the shapefile and isolate shapes
    shp = shapefile.Reader(path)
    shapes = shp.shapeRecords()

    startPointDict = {}
    endPointDict = {}
    reachCodeDict = {}
    # Stage 2: Associate a startpoint and endpoint with each shape in two dictionaries
    # for faster lookup times
    for sr in shapes:
        shape = sr.shape
        record = sr.record
        if shape.shapeType == 13:
            # We have a polylinez, good to add
            sp = shape.points[0] # Tuple of 2
            ep = shape.points[len(shape.points) - 1] # Tuple of 2
            
            placeInDict(startPointDict,sp,sr)
            placeInDict(endPointDict,ep,sr)
            reachCodeDict[record.ReachCode] = sr
        else:
            print("Unrecognized type!")
            break   
    
    return (startPointDict,endPointDict,reachCodeDict)



def findConnected(tridict,reachCode,export=True):
    '''
    Find all the lines connected to the line with the specific reachCode. In essence,
    isolating a Network which can be reached via reachCode.

    path [string]: Path of the shapefile
    reachCode [string]: ReachCode of the line desired

    Returns [Network]: Returns a connected network of Flow lines and fake Sites in between them
    '''
    def getTheOthers(dict,point,shaperc,lim=4):
        '''
        Returns list of ShapeRecords based on provided dict and template obj
        '''
        l = []
        for i in range(lim):
            hashy = getPosHash(point,i)
            try:
                obj = dict[hashy]
                if obj == shaperc:
                    continue
                # We found an 'other' that connects here, add it to list
                l.append(obj)
            except KeyError as identifier:
                break
        return l
    # Stage 2: Select proper shape based on reachCode
    try:
        shprc = tridict[2][reachCode]
        idCounter = 0
        siteDict = {}
        flowDict = {}      
        objQueue = [shprc]
        def determineExists(dict,point,limit=4):
            for i in range(limit):
                if getPosHash(point,i) in dict.keys():
                    return i
            return None
        # Stage 3: Go downwards initially as well as up
        while len(objQueue) > 0:
            shrek = objQueue.pop(0)
            # Try adding in my sites to the siteTable
            sp = shrek.shape.points[0]
            ep = shrek.shape.points[1]
            if not getPosHash(sp) in siteDict.keys():
                # Site not existing already, add it in
                idCounter += 1
                siteDict[getPosHash(sp)] = Site(idCounter,sp[0],sp[1],0,0)
                # Now we need to add all my neighbors to the queue
                
            if not getPosHash(ep) in siteDict.keys():
                idCounter += 1
                siteDict[getPosHash(ep)] = Site(idCounter,ep[0],ep[1],0,0)
                # Now we need to add all my neighbors to the queue
                
            if not shrek.record.ReachCode in flowDict.keys():
                flowRep = Flow(shrek.record.GNIS_ID_12,siteDict[getPosHash(sp)],
                siteDict[getPosHash(ep)],shrek.record.LengthKM,
                shrek.record.ReachCode,shrek.record.GNIS_Name)
                flowDict[shrek.record.ReachCode] = flowRep
            
            # For the startpoint, see if it is also the endpoint of others
            s_oth = getTheOthers(tridict[1],sp,shrek)
            # For the endpoint, see if it is also the startpoint of others or endpoint of others
            # HELP! THIS IS NOT WORKING >_<; it should get other lines connecting to this point, but
            # it says there are none!


          
        # FINAL Stage: Return a network given value set in dictionary      
        netty = Network(list(flowDict.values()),list(siteDict.values()))
        if export:
            # We need to export this network as a shapefile
            pass
        return netty
        
            
    except KeyError as identifier:
        # Error: That reach code is not found in any record!
        raise RuntimeError("findConnected() Reach Code provided does not exist in table!")
        return None

def extrapolateFocus(net,path):
    ''' Will overlay existing sites from sitefile .shp (as specified by path)
        and will then revise the net.

        net [Network]: Network of existing flowlines and intersections (should be unassigned ID's in sites)
        path [string]: Path of NYS_sites Shapefile

        Return Tuple(Of Network,Flags As Integer()): Network relegated to the upstream and downstream bounds specified by
        the incomming data points.  Also returns Flags to detail attributes of the new Network
        FLAGS ---->
            0x0000 NO FLAGS
            0x0001 SCENARIO A: (See Workflow.txt)
            0x0002 SCENARIO B: 
            0x0004 SCENARIO C:
    ''' 
    # Step 1: Gather geometric data
    
    # Step 2: Pass over to QGIS script (python 3.x) or a arcpy script (python 2.x)
    #           Basically perform either an intersect with features [lines,poinits]
    # Step 3: Return Network as limited by these points
    

if __name__ == "__main__":
    PATH = "./Data/SELakeOntario/SELakeONtario.shp"
    tridict = importShapefile_TriDict(PATH)
    net = findConnected(tridict,"04140101001065")
    extrapolateFocus(net,"p")
    print(net)