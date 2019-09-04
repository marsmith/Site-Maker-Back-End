def minDistance(dist, pathSet, net):
    min = sys.maxint
    
    for v in range(len(net.siteTable)):
        if dist[v] < min and pathSet[v] == False:
            min = dist[v]
            min_index = v
    return min_index

def calculateUpstreamDistances(net,sinkSite):
    dist = [sys.maxint] * len(net.siteTable)
    dist[sinkSite.id] = 0
    pathSet = [False] * len(net.siteTable)

    for n in range(len(net.siteTable)):
        #pick node with minimum distance that hasn't been processed
        u = minDistance(dist, pathSet, net)
        pathSet[u] = True

        for v in range(len(net.siteTable)):
            temp_dist = 0
            for flow in net.flowTable:
                if int(flow.upstreamSite.id) == v and int(flow.downstreamSite.id) == u:
                     temp_dist = flow.length
                
            if temp_dist > 0 and pathSet[v] == False and \
                dist[v] > dist[u] + temp_dist:
                dist[v] = dist[u] + temp_dist
                print str(v) + " dist:  " + str(dist[v])
