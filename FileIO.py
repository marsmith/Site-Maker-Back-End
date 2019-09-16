from Precompiler import *


def exportNetwork(net,name,path):
    path = str(path).rstrip("/")
    fileobject = open("{0}/{1}_sites.txt".format(path,name), "w")
    for site in net.siteTable:
        string = "%d, %f, %f\n" %(site.id, site.latLong.srcLat, site.latLong.srcLong)
        fileobject.write(string)        
    fileobject.close()
    fileobject = open("{0}/{1}_flows.txt".format(path,name), "w")
    for flow in net.flowTable:
        string = "%d, %d, %.10f\n" %(flow.upstreamSite.id, flow.downstreamSite.id, flow.length)
        fileobject.write(string)
    fileobject.close()