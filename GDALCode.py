from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst
import os

def isolateNetwork(folderPath,siteLayerName,lineLayerName,userClickLayerName):
    path = folderPath + "\\" + lineLayerName + "\\" + lineLayerName + ".shp"
    path_userClick = folderPath + "\\" + userClickLayerName + "\\" + userClickLayerName + ".shp"
    dataSource = ogr.Open(path)
    shpdriver = ogr.GetDriverByName('ESRI Shapefile')
    layer = dataSource.GetLayer()
    featureCount = layer.GetFeatureCount()
    print ("Number of features in %s: %d" % (os.path.basename(path),featureCount))
    
    # Buffer around userClick
    print("Now buffer around userClick")
    pointDataSource = ogr.Open(path_userClick)
    pl = pointDataSource.GetLayer()
    assert (len(pl) == 1) # There should only be one user click inside the shapefile
    point = pl.GetNextFeature()
    
    ingeom = point.GetGeometryRef()
    geomBuffer = ingeom.Buffer(10.0) # Buffer 10 meters around the geometry
 
    # Load Selected Sites

    # Intersect of BUFFER and SITES
    
    # IF #INTER_SITES < 2 (expand circle)?

    # Load Selected Lines

    # Intersect of BUFFER and LINES

    # Split INTER_LINES based on points (INTER_SITES)

    # Navigate SPLIT_INTER_LINES until we reach INTER_SITES. 
    # return network
    

    print(linesDataset)
def importSites():
    pass

def importLines():
    pass


if __name__ == "__main__":
   isolateNetwork("C:\\Users\\mpanozzo\\Desktop\\GDAL Data","SitesSnapped","NHDFlowline","USER_CLICK")
