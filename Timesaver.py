from GDALCode import *


def determineNewSiteID_Timely(longg,latt,folderPath,siteLayerName,lineLayerName,numSecAllowed=30):
    x = threading.Thread(target=determineNewSiteID,args=(longg,latt,folderPath,siteLayerName,lineLayerName),daemon=True)
    x.start()
    time.sleep(numSecAllowed)
    sys.exit()

    
    