from Precompiler import importJSON
from Precompiler import isolateNet
from Precompiler import setupSiteSafety
from Precompiler import calculateFaucets
from Precompiler import calculateUpstreamDistances
from Precompiler import Network

'''
Module for creating networks based on the
areas between real sites in the NHD & Sitefile combo.
'''



def generateNetwork(fp):
    
    dictt = importJSON("Data/SmallNet001.json")
    net = isolateNet(dictt,True) 
    sinks = calculateSink(net)
    #removeUseless(net)
    assert(len(sinks) == 1)
    setupSiteSafety(net)
    faucets = calculateFaucets(net)
    calculateUpstreamDistances(net,faucets)
    net.recalculateTotalLength()
    return net
'