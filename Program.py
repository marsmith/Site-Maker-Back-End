from Precompiler import *
import NetworkCrafter
from MultiNetwork import *
import DataIO
import Visualizer
import test
if __name__ == "__main__":
    site = Site(0,0,0,0)
    #PreChanges: 3:40
    dict = NetworkCrafter.importJSON("Data/SmallNet001.json")
    net = NetworkCrafter.isolateNet(dict,True)
    sinks = net.calculateSink()    
    net.setupSiteSafety()
    net.calculateFaucets()
    net.calculateUpstreamDistances()
    print("Hey!")
    pSNA(net,SiteID(1001,9999,None))
    DataIO.networkToCSV(net,"C:\\Users\\mpanozzo\\Documents\\SITE_TABLE.csv","C:\\Users\\mpanozzo\\Documents\\FLOW_TABLE.csv")
    t = test.TestPrecompiler()
    t.create_files(net)
    Visualizer.create_visuals("hello")
