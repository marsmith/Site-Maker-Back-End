'''
Module for creating networks based on the
areas between real sites in the NHD & Sitefile combo.
'''
from Precompiler import *

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


def generateNetworks(fp):    
    
    dictt = importJSON(fp)
    net = isolateNet(dictt,True) 
    sinks = net.calculateSink()    
    if len(sinks) > 1:
        # We will have more than one network. Lets find them all
        pass
    else:
        net.setupSiteSafety()
        faucets = net.calculateFaucets()
        net.calculateUpstreamDistances()
        net.recalculateTotalLength()
        return net
    
