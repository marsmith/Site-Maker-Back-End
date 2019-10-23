from Precompiler import *
import unittest
import numpy
from Visualizer import *


''' The best way to do testing will still involve 
human verification, but this ensures there are no minor bugs
'''

EPSILON = 0.01

class TestPrecompiler(unittest.TestCase):
    def SiteLoader(self, filepath):
        jsonDict = open(filepath,"r").read()
        jsonDict = json.loads(jsonDict)
        fList = jsonDict["features"]
        fileobject = open("RealSites.txt", "w")

        for geomObj in fList:
            coord = geomObj['geometry']['coordinates']
            site_no = geomObj['properties']['site_no']
            string = "%s, %f, %f\n" %(site_no, coord[0], coord[1])
            fileobject.write(string)
        fileobject.close()

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

    def verifySink(self,net):
        sinks = calculateSink(net)
        assert(len(sinks)) == 1
        return sinks[0]

    def verifyFaucets(self,net):
        faucets = calculateFaucets(net)
        assert(len(faucets) < len(net.siteTable))
        return faucets

    def verifyTotalUpstreamDist(self,net,faucets=None):
        if faucets is None:
            faucets = self.verifyFaucets(net)
        return calculateUpstreamDistances(net,faucets)

    def verifyLowestUpstreamDist(self,net):
        sink = self.verifySink(net)
        # Totals must be calculated beforehand        
        cs = sink.connectedSites()
        assert(len(cs) == 1)
        assert(cs[0][1] == UPSTREAM_CON)
        net.recalculateTotalLength()
        diff = abs(cs[0][2].thisAndUpstream - net.totalSize)
        assert(diff <= EPSILON)

    def verifyImport(self,jsonPath,remove2s=False):
        dictt = importJSON(jsonPath)
        assert(not dictt is None)
        net = isolateNet(dictt) 
        if remove2s:
            removeUseless(net)
        sink = self.verifySink(net)
        setupSiteSafety(net)
        faucets = self.verifyFaucets(net)
        self.verifyTotalUpstreamDist(net)
        self.verifyLowestUpstreamDist(net)
        return (net,sink,faucets)
        # Check sites were all setup

    def verifyAllNumbered(self,net):
        for s in net.siteTable:
            assert(s.assignedID > 0)
        
    def test_smallNet(self):
        netTup = self.verifyImport('Data/SmallNet001.json')
        maxID = SiteID(1001)
        pSNA(netTup[0],maxID,netTup[1])
        
        self.verifyAllNumbered(netTup[0])
        self.SiteLoader("Data/snapped-site-test-subset.json")
        self.create_files(netTup[0])
        #create_visuals("SmallNet001")
        


    def test_loop001(self):
        netTup = self.verifyImport('Data/TrickyLoops001.json')
        maxID = SiteID(1001)
        pSNA(netTup[0],maxID,netTup[1])
        calcStraihler(netTup[0])
        self.verifyAllNumbered(netTup[0])
        self.create_files(netTup[0])
        create_visuals("TrickyLoops001")
        

    def test_loop002(self):
        netTup = self.verifyImport('Data/LoopTest001-NHDSubset.json')
        maxID = SiteID(1001)
        #calcStraihler(netTup[0])
        pSNA(netTup[0],maxID,netTup[1])
        
        self.verifyAllNumbered(netTup[0])
        self.create_files(netTup[0])
        #create_visuals("LoopTest001-NHDSubset")

