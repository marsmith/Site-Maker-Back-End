from GDALCode import *
import multiprocessing as mp

def recoverReturn(longg,latt,folderPath,siteLayerName,lineLayerName,returnDict):
    returnDict["data"] = determineNewSiteID(longg,latt,folderPath,siteLayerName,lineLayerName)



def determineNewSiteID_Timely(longg,latt,folderPath,siteLayerName,lineLayerName,numSecAllowed=30):
    man = mp.Manager()
    rD = man.dict()
    x = mp.Process(target=recoverReturn,args=(longg,latt,folderPath,siteLayerName,lineLayerName,rD),daemon=True)
    
    timeSlept = 0
    x.start()   
    while timeSlept < numSecAllowed:
        if x.is_alive():
            time.sleep(0.1)
        else:
            break
            time.sleep(0.1)
        timeSlept += 0.1
    if x.is_alive():
        x.terminate()
    if "data" in rD.keys():
        return rD["data"]
    else:
        raise RuntimeError("determineNewSiteID_Timely() [Error]: Could not determine ID in time")


if __name__ == "__main__":
    folderPath = "C:\\Users\\mpanozzo\\Desktop\\GDAL_DATA_PR"
    siteLayerName = "ProjectedSites"
    lineLayerName = "NHDFlowline_Project_SplitLin3"
    longg = -73.52481561 #-76.3612354
    latt = 41.1930218#43.4810611 
    try:
        newID = determineNewSiteID_Timely(longg,latt,folderPath,siteLayerName,lineLayerName,1) 
        print(newID)
    except Exception as e:
        print(e)
   
    