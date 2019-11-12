from GDALCode import *
import multiprocessing

def determineNewSiteID_Timely(longg,latt,folderPath,siteLayerName,lineLayerName,numSecAllowed=30):
    x = threading.Thread(target=determineNewSiteID,args=(longg,latt,folderPath,siteLayerName,lineLayerName),daemon=True)
    x.start()
    time.sleep(numSecAllowed)
    try:
        print("EEE")
        return
    except Exception as e:
        print(e)


if __name__ == "__main__":
    folderPath = "C:\\Users\\mpanozzo\\Desktop\\GDAL_DATA_PR"
    siteLayerName = "ProjectedSites"
    lineLayerName = "NHDFlowline_Project_SplitLin3"
    longg = -73.52481561
    latt = 41.1930218
    newID = determineNewSiteID_Timely(longg,latt,folderPath,siteLayerName,lineLayerName) 
    