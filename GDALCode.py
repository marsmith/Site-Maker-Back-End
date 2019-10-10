from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst
import os

def isolateNetwork(folderPath,siteLayerName,lineLayerName,userClickLayerName):
    # Load Lines
    path = folderPath + "\\" + lineLayerName + "\\" + lineLayerName + ".shp"
    path_userClick = folderPath + "\\" + userClickLayerName + "\\" + userClickLayerName + ".shp"
    path_sites = folderPath + "\\" + siteLayerName + "\\" + siteLayerName + ".shp"
    dataSource = ogr.Open(path)
    shpdriver = ogr.GetDriverByName('ESRI Shapefile')
    layer = dataSource.GetLayer()
    

    

    # Buffer around userClick
    print("Now buffer around userClick")
    pointDataSource = ogr.Open(path_userClick)
    pl = pointDataSource.GetLayer()
    assert (len(pl) == 1) # There should only be one user click inside the shapefile
    point = pl.GetNextFeature()
    # Reproject
    targRef = osr.SpatialReference()
    targRef.ImportFromEPSG(26918) # NY State Projection
    
    # Get the pointlayer projection
    point_spatialRef = pl.GetSpatialRef()

    transform = osr.CoordinateTransformation(point_spatialRef,targRef)



    ingeom = point.GetGeometryRef()
    ingeom.Transform(transform)
    geomBuffer = ingeom.Buffer(10.0) # Buffer 10 meters around the geometry
 
    # Load Selected Sites
    sitesDataSource = ogr.Open(path_sites)
    sl = sitesDataSource.GetLayer()

    # Intersect of BUFFER and SITES
    interSites = []
    for site in sl:
        ingeom_site = site.GetGeometryRef()
        if ingeom_site.Intersect(geomBuffer):
            # This site is inside the buffer!
            interSites.append(site)

    # IF #INTER_SITES < 2 (expand circle)?
    if len(interSites) < 2:
        print("UUUUUUh")
    # Load Selected Lines

    # Intersect of BUFFER and LINES

    # Split INTER_LINES based on points (INTER_SITES)

    # Navigate SPLIT_INTER_LINES until we reach INTER_SITES. 
    # return network
    

    print(linesDataset)


if __name__ == "__main__":
   isolateNetwork("C:\\Users\\mpanozzo\\Desktop\\GDAL Data","SitesSnapped","NHDFlowline","USER_CLICK")
