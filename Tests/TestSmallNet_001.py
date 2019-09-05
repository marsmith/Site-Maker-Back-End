import CreateStructure as CS

if __name__ == "__main__":
    dictt = CS.importJSON("../Data/SmallNet001.json")
    net = CS.isolateNet(dictt)    
    sinks = CS.calculateSink(net)
    CS.removeUseless(net)
    assert(len(sinks) == 1)
    faucets = CS.calculateFaucets(net)
    CS.calculateUpstreamDistances(net,faucets)
    net.recalculateTotalLength()

    CS.pSNA(net,CS.SiteID(1001,9999,None),sinks[0])
    print("Done!")