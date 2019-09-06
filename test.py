from Precompiler import *
import unittest
import numpy


''' The best way to do testing will still involve 
human verification, but this ensures there are no minor bugs
'''

EPSILON = 0.01

class TestPrecompiler(unittest.TestCase):
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
        confluenceReferenceIDAssign(net,faucets)
        self.verifyAllNumbered(netTup[0])
        
    ''' Test on TrickyLoops001; 
    '''
    def test_loop001(self):
        netTup = self.verifyImport('Data/TrickyLoops001.json')
        maxID = SiteID(1001)
        pSNA(netTup[0],maxID,netTup[1])
        confluenceReferenceIDAssign(net,faucets)
        self.verifyAllNumbered(netTup[0])
        print("Breakpoint")
        
    def test_loop002(self):
        netTup = self.verifyImport('Data/LoopTest001-NHDSubset.json')
        maxID = SiteID(1001)
        pSNA(netTup[0],maxID,netTup[1])
        confluenceReferenceIDAssign(net,faucets)
        self.verifyAllNumbered(netTup[0])



    
