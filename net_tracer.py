from Precompiler import *


def net_tracer(network):
    real_sites_counter = 0
    for site in network.siteTable:
        if site.isReal:
                real_sites_counter += 1
                real_site = site
    print(real_sites_counter)
    if real_sites_counter == 1:
        queue = [real_site]
        while (queue):
            curr = queue.pop()
            for flow in network.flowTable:
                if flow.upstreamSite == curr:
                    current_flow = flow
                    break
            
            for flow in network.flowTable:
                if flow.downstreamSite == current_flow.downstreamSite:
                    other_flow = flow
            
            if current_flow.thisAndUpstream < other_flow.thisAndUpstream:
                #Assign confluence
                current_flow.downstreamSite.id == current_flow.upstreamSite.id + current_flow.thisAndUpstream
                #assign other upstream site
                other_flow.upstreamSite.id = current_flow.upstreamSite.id - other_flow.thisAndUpstream
            
            else:
                #Assign confluence
                current_flow.downstreamSite.id == current_flow.upstreamSite.id + current_flow.thisAndUpstream + other_flow.thisAndUpstream
                #Assign other upstream site
                other_flow.upstreamSite.id = other_flow.downstreamSite.id - other_flow.thisAndUpstream

            queue.append(current_flow.downstreamSite)
            
