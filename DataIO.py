from Precompiler import *

import pyodbc

def networkToAccess(net,dbPath): 
    print([x for x in pyodbc.drivers()])

    conn_str = r"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={0}".format(dbPath)  
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    for site in net.siteTable:
        # Obtain a flowscon string list
        flstr = ""
        for fl in site.flowsCon:
            flstr = flstr + str(fl.id) + ";"
        flstr.rstrip(";")
        sqlStr = 'INSERT INTO SITE_TABLE\nVALUES ({0}, {1}, {2}, "{3}", {4}, "{5}", "{6}");'.format(
            site.id,site.latLong.srcLat,site.latLong.srcLong,site.downwardRefID,True,flstr,str(site.assignedID)
        )

        cursor.execute(sqlStr)

def networkToCSV(net,siteOUT="./SITE_TABLE.csv",flowOUT="./FLOW_TABLE.csv"):
    fileHandle = open(siteOUT,"w")
    for site in net.siteTable:
        flstr = ""
        for fl in site.flowsCon:
            flstr = flstr + str(fl.id) + ";"
        flstr.rstrip(";")
        formWtr =  str("%08d"%site.assignedID.watershed)
        insstr = '{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}\n'.format(
            site.id,site.latLong.srcLat,site.latLong.srcLong,site.downwardRefID,site.isReal,flstr,str(site.assignedID),formWtr)
        fileHandle.write(insstr)
    fileHandle.close()
    fileHandle = open(flowOUT,"w")
    for flow in net.flowTable:
        insstr = '{0}, {1}, {2}, {3}, {4}, {5}, {6}\n'.format(
            flow.id,flow.upstreamSite.id,flow.downstreamSite.id,flow.length,flow.reachCode,"",flow.thisAndUpstream
        )
        fileHandle.write(insstr)
    fileHandle.close()

