from Precompiler import *
import unittest
import numpy
class TestPrecompiler(unittest.TestCase):
    def verifySink(self,net):
        sinks = calculateSink(net)
        assert(len(sink)) == 1
        return sinks[0]
        
    def verifyUpstreamDist(self,net):
        sink = self.verifySink(net)
        cs = sink.connectedSites()
        assert(len(cs) == 1)
        assert(cs[0][1] == UPSTREAM_CON)
        assert(numpy.floor(cs[0][2].thisAndUpstream) == numpy.floor(net.totalSize))

    def test_smallNet(self):
        pass
    ''' Test on TrickyLoops001; 
    '''
    def test_loop001(self):

    
