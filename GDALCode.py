from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst
import os

def isolateNetwork(folderPath,siteLayerName,lineLayerName,x,y):
    # Load Lines
    path = folderPath + "\\" + lineLayerName + "\\" + lineLayerName + ".shp"
    
    path_sites = folderPath + "\\" + siteLayerName + "\\" + siteLayerName + ".shp"
    
    
    # Buffer around userClick
    print("Now buffer around userClick")
    oRef = osr.SpatialReference()
    oRef.ImportFromEPSG(4326)

    # Reproject
    targRef = osr.SpatialReference()
    targRef.ImportFromEPSG(26918) # NY State Projection
    
    # Create point from x,y and targRef
    ctran = osr.CoordinateTransformation(oRef,targRef)
    [p_lng,p_lat,z] = ctran.TransformPoint(x,y)
    inputPointProj = ogr.Geometry(ogr.wkbPoint)
    inputPointProj.SetPoint_2D(0,p_lng,p_lat)


    print("I got to here")

    geomBuffer = inputPointProj.Buffer(10000) # Buffer 10 meters around the geometry
 
    # Load Selected Sites
    sitesDataSource = ogr.Open(path_sites)
    sl = sitesDataSource.GetLayer()
    ctran = osr.CoordinateTransformation(sl.GetSpatialRef(),targRef)
    
    # Intersect of BUFFER and SITES
    interSites = []
    for site in sl:
        ingeom_site = site.GetGeometryRef()
        ingeom_site.Transform(ctran)
        if ingeom_site.Intersect(geomBuffer):
            # This site is inside the buffer!
            interSites.append(site)

    # IF #INTER_SITES < 2 (expand circle)?
    print(len(interSites))
    if len(interSites) < 2:
        print("UUUUUUh")
    
    # Save sites that were inside the circle as a layer


    # Load Selected Lines
    dataSource = ogr.Open(path)
    shpdriver = ogr.GetDriverByName('ESRI Shapefile')
    linesLayer = dataSource.GetLayer()
    interLines = []
    # Intersect of BUFFER and LINES
    for line in linesLayer:
        ingeom_line = line.GetGeometryRef()
        ingeom_line.Transform(ctran)
        if ingeom_line.Intersect(geomBuffer):
            interLines.append(line)

    


    # Split INTER_LINES based on points (INTER_SITES)

    # Navigate SPLIT_INTER_LINES until we reach INTER_SITES. 
    # return network
    

    print(linesDataset)


if __name__ == "__main__":
   isolateNetwork("C:\\Users\\mpanozzo\\Desktop\\GDAL Data","SitesSnapped","NHDFlowline",-73.939645996,42.378012068)
