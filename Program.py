from Precompiler import *
from NetworkCrafter import *
from MultiNetwork import *

if __name__ == "__main__":
    net = NetworkCrafter.generateNetworks("Data/OneidaFlowSimplified.json")
    pSNA(net,SiteID(1001,9999,None))
    DataIO.networkToCSV(net,"C:\\Users\\mpanozzo\\Documents\\SITE_TABLE.csv","C:\\Users\\mpanozzo\\Documents\\FLOW_TABLE.csv")
    t = test.TestPrecompiler()
    t.create_files(net)
    Visualizer.create_visuals("hello")
