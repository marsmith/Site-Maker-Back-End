from Precompiler import *
import unittest
import numpy
from Visualizer import *
from GDALCode import *


''' The best way to do testing will still involve 
human verification, but this ensures there are no minor bugs
'''

EPSILON = 0.01

class TestPrecompiler(unittest.TestCase):
#     def SiteLoader(self, filepath):
#         jsonDict = open(filepath,"r").read()
#         jsonDict = json.loads(jsonDict)
#         fList = jsonDict["features"]
#         fileobject = open("RealSites.txt", "w")

#         for geomObj in fList:
#             coord = geomObj['geometry']['coordinates']
#             site_no = geomObj['properties']['site_no']
#             string = "%s, %f, %f\n" %(site_no, coord[0], coord[1])
#             fileobject.write(string)
#         fileobject.close()

    def create_files(self, net):
        fileobject = open("Sites.txt", "w")
        for site in net.siteTable:
            
            strr = "{0}, {1:f}, {2:f}, {3}, {4}\n".format(site.id, site.latLong.srcLat, site.latLong.srcLong, str(site.assignedID), str(site.downwardRefID))
            #string = "%d, %f, %f, %s, %s\n" %(site.id, site.latLong.srcLat, site.latLong.srcLong, str(site.assignedID), str(site.downwardRefID))
            fileobject.write(strr)
        fileobject.close()
        fileobject = open("Flows.txt", "w")
        for flow in net.flowTable:
            strr = "{0}, {1}, {2:f}, {3:f}, {4}\n".format(flow.upstreamSite.id, flow.downstreamSite.id, flow.length, flow.thisAndUpstream, flow.straihler)
            #string = "%d, %d, %f, %f, %d \n" %(flow.upstreamSite.id, flow.downstreamSite.id, flow.length, flow.thisAndUpstream, flow.straihler)
            fileobject.write(strr)
        fileobject.close()

#     def verifySink(self,net):
#         sinks = calculateSink(net)
#         assert(len(sinks)) == 1
#         return sinks[0]

#     def verifyFaucets(self,net):
#         faucets = calculateFaucets(net)
#         assert(len(faucets) < len(net.siteTable))
#         return faucets

#     def verifyTotalUpstreamDist(self,net,faucets=None):
#         if faucets is None:
#             faucets = self.verifyFaucets(net)
#         return calculateUpstreamDistances(net,faucets)

#     def verifyLowestUpstreamDist(self,net):
#         sink = self.verifySink(net)
#         # Totals must be calculated beforehand        
#         cs = sink.connectedSites()
#         assert(len(cs) == 1)
#         assert(cs[0][1] == UPSTREAM_CON)
#         net.recalculateTotalLength()
#         diff = abs(cs[0][2].thisAndUpstream - net.totalSize)
#         assert(diff <= EPSILON)

#     def verifyImport(self,jsonPath,remove2s=False):
#         dictt = importJSON(jsonPath)
#         assert(not dictt is None)
#         net = isolateNet(dictt) 
#         if remove2s:
#             removeUseless(net)
#         sink = self.verifySink(net)
#         setupSiteSafety(net)
#         faucets = self.verifyFaucets(net)
#         self.verifyTotalUpstreamDist(net)
#         self.verifyLowestUpstreamDist(net)
#         return (net,sink,faucets)
#         # Check sites were all setup

#     def verifyAllNumbered(self,net):
#         for s in net.siteTable:
#             assert(s.assignedID > 0)
        
#     def test_smallNet(self):
#         netTup = self.verifyImport('Data/SmallNet001.json')
#         maxID = SiteID(1001)
#         pSNA(netTup[0],maxID,netTup[1])
        
#         self.verifyAllNumbered(netTup[0])
#         self.SiteLoader("Data/snapped-site-test-subset.json")
#         self.create_files(netTup[0])
#         #create_visuals("SmallNet001")
        


#     def test_loop001(self):
#         netTup = self.verifyImport('Data/TrickyLoops001.json')
#         maxID = SiteID(1001)
#         pSNA(netTup[0],maxID,netTup[1])
#         calcStraihler(netTup[0])
#         self.verifyAllNumbered(netTup[0])
#         self.create_files(netTup[0])
#         create_visuals("TrickyLoops001")
        

#     def test_loop002(self):
#         netTup = self.verifyImport('Data/LoopTest001-NHDSubset.json')
#         maxID = SiteID(1001)
#         #calcStraihler(netTup[0])
#         pSNA(netTup[0],maxID,netTup[1])
        
#         self.verifyAllNumbered(netTup[0])
#         self.create_files(netTup[0])
#         #create_visuals("LoopTest001-NHDSubset")

class TestProject(unittest.TestCase):
    def checkIfSiteExists(self,folderPath,siteLayerName,siteID):
        path_sites = str(folderPath) + "/" + str(siteLayerName) + "/" + str(siteLayerName) + ".shp"

        sitesDataSource = ogr.Open(path_sites)
        sl = sitesDataSource.GetLayer()
        siteNumber_index = sl.GetLayerDefn().GetFieldIndex("site_no")
        ffDict = {} # Stores the first four
        
        sitStr = str(siteID)
        for site in sl:
            ff = site.GetFieldAsString(siteNumber_index)
            if ff == sitStr:
                return True
        return False


    def test_NoSitesAround1(self):
        x = -75.5738275
        y = 42.084898
        folderPath = "/Users/nicknack/Downloads/GDAL_DATA_PR"
        siteLayerName = "ProjectedSites"
        lineLayerName = "NHDFlowline_Project_SplitFINAL"
        newSite = determineNewSiteID(x,y,folderPath,siteLayerName,lineLayerName)
        print(newSite)

        if checkIfSiteExists(folderPath, siteLayerName, newSite):
            print("This site already exists!!!! X(")
  

    def test_NoSitesAround2(self):
        x = -74.7391559
        y = 43.9835929

        folderPath = "/Users/nicknack/Downloads/GDAL_DATA_PR"
        siteLayerName = "ProjectedSites"
        lineLayerName = "NHDFlowline_Project_SplitFINAL"
        
        newSite = determineNewSiteID(x,y,folderPath,siteLayerName,lineLayerName)
        print(newSite)
        if checkIfSiteExists(folderPath, siteLayerName, newSite):
            print("This site already exists!!!! X(")


    def test_OneSite1(self):
        x = -73.6648475
        y = 44.9726123

        folderPath = "/Users/nicknack/Downloads/GDAL_DATA_PR"
        siteLayerName = "ProjectedSites"
        lineLayerName = "NHDFlowline_Project_SplitFINAL"

        newSite = determineNewSiteID(x,y,folderPath,siteLayerName,lineLayerName)
        print(newSite)
        if checkIfSiteExists(folderPath, siteLayerName, newSite):
            print("This site already exists!!!! X(")

    def test_OneSite2(self):
        x = -74.0457767
        y = 43.7390809

        folderPath = "/Users/nicknack/Downloads/GDAL_DATA_PR"
        siteLayerName = "ProjectedSites"
        lineLayerName = "NHDFlowline_Project_SplitFINAL"

        newSite = determineNewSiteID(x,y,folderPath,siteLayerName,lineLayerName)
        print(newSite)
        if checkIfSiteExists(folderPath, siteLayerName, newSite):
            print("This site already exists!!!! X(")

    def test_TwoOrMore1(self):
        x = -75.2829214
        y = 43.9238472

        folderPath = "/Users/nicknack/Downloads/GDAL_DATA_PR"
        siteLayerName = "ProjectedSites"
        lineLayerName = "NHDFlowline_Project_SplitFINAL"

        newSite = determineNewSiteID(x,y,folderPath,siteLayerName,lineLayerName)
        print(newSite)
        if checkIfSiteExists(folderPath, siteLayerName, newSite):
            print("This site already exists!!!! X(")

    def test_TwoOrMore2(self):
        x = -74.0535743
        y = 43.9645663

        folderPath = "/Users/nicknack/Downloads/GDAL_DATA_PR"
        siteLayerName = "ProjectedSites"
        lineLayerName = "NHDFlowline_Project_SplitFINAL"

        newSite = determineNewSiteID(x,y,folderPath,siteLayerName,lineLayerName)
        print(newSite)
        if checkIfSiteExists(folderPath, siteLayerName, newSite):
            print("This site already exists!!!! X(")

    def test_TwoOrMore3(self):
        x = -74.7935758
        y = 43.3986814

        folderPath = "/Users/nicknack/Downloads/GDAL_DATA_PR"
        siteLayerName = "ProjectedSites"
        lineLayerName = "NHDFlowline_Project_SplitFINAL"

        newSite = determineNewSiteID(x,y,folderPath,siteLayerName,lineLayerName)
        print(newSite)
        if checkIfSiteExists(folderPath, siteLayerName, newSite):
            print("This site already exists!!!! X(")

    def test_IsolatedNet1(self):
        x = -76.3612354  #04249020
        y = 43.4810611

        folderPath = "/Users/nicknack/Downloads/GDAL_DATA_PR"
        siteLayerName = "ProjectedSites"
        lineLayerName = "NHDFlowline_Project_SplitFINAL"

        newSite = determineNewSiteID(x,y,folderPath,siteLayerName,lineLayerName)
        print(newSite)
        if checkIfSiteExists(folderPath, siteLayerName, newSite):
            print("This site already exists!!!! X(")

    def test_IsolatedNet2(self):
        x = -74.7125772
        y = 43.2162956

        folderPath = "/Users/nicknack/Downloads/GDAL_DATA_PR"
        siteLayerName = "ProjectedSites"
        lineLayerName = "NHDFlowline_Project_SplitFINAL"

        newSite = determineNewSiteID(x,y,folderPath,siteLayerName,lineLayerName)
        print(newSite)
        if checkIfSiteExists(folderPath, siteLayerName, newSite):
            print("This site already exists!!!! X(")

    def test_IsolatedNet3(self):
        x = -74.4279059
        y = 41.2865867

        folderPath = "/Users/nicknack/Downloads/GDAL_DATA_PR"
        siteLayerName = "ProjectedSites"
        lineLayerName = "NHDFlowline_Project_SplitFINAL"

        newSite = determineNewSiteID(x,y,folderPath,siteLayerName,lineLayerName)
        print(newSite)
        if checkIfSiteExists(folderPath, siteLayerName, newSite):
            print("This site already exists!!!! X(")
    
    def test_MartySite1(self):
        x = -74.0136461 # Chubb River, returned 0427389473
        y = 44.2623416
        folderPath = "/Users/nicknack/Downloads/GDAL_DATA_PR"
        siteLayerName = "ProjectedSites"
        lineLayerName = "NHDFlowline_Project_SplitFINAL"

        newSite = determineNewSiteID(x,y,folderPath,siteLayerName,lineLayerName)
        print(newSite)
        if checkIfSiteExists(folderPath, siteLayerName, newSite):
            print("This site already exists!!!! X(")


    def test_MartySite2(self):
        x = -73.9204767 # Unnamed Trib #1 (upstream side), returned 0427399889
        y = 44.3030970 
        folderPath = "/Users/nicknack/Downloads/GDAL_DATA_PR"
        siteLayerName = "ProjectedSites"
        lineLayerName = "NHDFlowline_Project_SplitFINAL"

        newSite = determineNewSiteID(x,y,folderPath,siteLayerName,lineLayerName)
        print(newSite)
        if checkIfSiteExists(folderPath, siteLayerName, newSite):
            print("This site already exists!!!! X(")

    def test_MartySite3(self):
        x =  -73.9205663 #Unnamed Trib #1 (downstream side) 0427399897
        y = 44.3038121
        folderPath = "/Users/nicknack/Downloads/GDAL_DATA_PR"
        siteLayerName = "ProjectedSites"
        lineLayerName = "NHDFlowline_Project_SplitFINAL"

        newSite = determineNewSiteID(x,y,folderPath,siteLayerName,lineLayerName)
        print(newSite)
        if checkIfSiteExists(folderPath, siteLayerName, newSite):
            print("This site already exists!!!! X(")

    def test_MartySite4(self):
        x =  -73.9123839   # Unnamed Trib #2 (upstream side) 04273842
        y = 44.2371825
        folderPath = "/Users/nicknack/Downloads/GDAL_DATA_PR"
        siteLayerName = "ProjectedSites"
        lineLayerName = "NHDFlowline_Project_SplitFINAL"

        newSite = determineNewSiteID(x,y,folderPath,siteLayerName,lineLayerName)
        print(newSite)
        if checkIfSiteExists(folderPath, siteLayerName, newSite):
            print("This site already exists!!!! X(")

    def test_MartySite5(self):
        x =  -73.9133175 # Unnamed Trib #2 (downstream side) 04273840
        y = 44.2363550
        folderPath = "/Users/nicknack/Downloads/GDAL_DATA_PR"
        siteLayerName = "ProjectedSites"
        lineLayerName = "NHDFlowline_Project_SplitFINAL"

        newSite = determineNewSiteID(x,y,folderPath,siteLayerName,lineLayerName)
        print(newSite)
        if checkIfSiteExists(folderPath, siteLayerName, newSite):
            print("This site already exists!!!! X(")

    def test_MartySite6(self):
        x = -73.8664487 # Sentinel Trib (downstream side) Returned 0427405868
        y = 44.3492810
        folderPath = "/Users/nicknack/Downloads/GDAL_DATA_PR"
        siteLayerName = "ProjectedSites"
        lineLayerName = "NHDFlowline_Project_SplitFINAL"

        newSite = determineNewSiteID(x,y,folderPath,siteLayerName,lineLayerName)
        print(newSite)
        if checkIfSiteExists(folderPath, siteLayerName, newSite):
            print("This site already exists!!!! X(")

    def test_MartySite7(self):
        x =  -73.8689959 # Sentinel Trib (upstream side) Returned 04274058
        y = 44.3470288
        folderPath = "/Users/nicknack/Downloads/GDAL_DATA_PR"
        siteLayerName = "ProjectedSites"
        lineLayerName = "NHDFlowline_Project_SplitFINAL"

        newSite = determineNewSiteID(x,y,folderPath,siteLayerName,lineLayerName)
        print(newSite)
        if checkIfSiteExists(folderPath, siteLayerName, newSite):
            print("This site already exists!!!! X(")
