from Precompiler import *


def net_tracer(network):
    '''
    Returns a list of sites which are along the real->sink chain
    '''
    real_sites_counter = 0
    rsc = [] # real to sink chain
    for site in network.siteTable:
        if site.isReal:
                real_sites_counter += 1
                real_site = site
    print(real_sites_counter)
    if real_sites_counter == 1:
        queue = [real_site]
        while (queue):
            curr = queue.pop()
            
            conTup = curr.connectedSites()
            
            for con in conTup:
                if con[1] == DOWNSTREAM_CON:
                    current_flow = con[2]
                    foundDown = True # We found a new downstream
            
            
            dsDest = current_flow.downstreamSite
            # Get the other flow which is upstream of the shared confluence
            conTup = dsDest.connectedSites()
            numUpStr = 0
            for con in conTup:
                if con[1] == UPSTREAM_CON and con[0] != curr:
                    other_flow = con[2]
                    numUpStr += 1
            
            # Special cases -----
            if not (current_flow.downstreamSite.assignedID is -1 or current_flow.downstreamSite.assignedID is None ):
                    # Already assigned! Do not do anything more
                continue # So we dont add to the queue again
            if dsDest == network.calculateSink()[0]:
                # The next site is a sink downstream; apply special rule
                dsDest.assignedID = curr.assignedID + current_flow.length
                break


            if current_flow.thisAndUpstream < other_flow.thisAndUpstream:
                # current <= other
                if (curr.assignedID is -1 or curr.assignedID is None ):
                    r = curr.id
                else:
                    r = curr.assignedID
                l = r - other_flow.thisAndUpstream
                
                current_flow.downstreamSite.assignedID =  r + current_flow.length # Conf. ID

                if curr == real_site:
                    current_flow.downstreamSite.downwardRefID = r

                #assign other upstream site
                #other_flow.upstreamSite.id = current_flow.upstreamSite.id - other_flow.thisAndUpstream
            
            else:
                # current > other
                if (curr.assignedID is -1 or curr.assignedID is None ):
                    l = curr.id
                else:
                    l = curr.assignedID

                r = l + current_flow.length                
                current_flow.downstreamSite.assignedID = r + other_flow.thisAndUpstream
                #current_flow.downstreamSite.downwardRefID = r

                #Assign other upstream site
                #other_flow.upstreamSite.id = other_flow.downstreamSite.id - other_flow.thisAndUpstream

            queue.append(current_flow.downstreamSite)
            rsc.append(current_flow.downstreamSite)
    return rsc

            
