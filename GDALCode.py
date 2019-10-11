from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst
import os
import folium


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
            interSites.append((site,ingeom_site))

    # IF #INTER_SITES < 2 (expand circle)?
    print(len(interSites))
    if len(interSites) < 2:
        print("UUUUUUh")
   
    # Load Selected Lines
    dataSource = ogr.Open(path)
    shpdriver = ogr.GetDriverByName('ESRI Shapefile')
    linesLayer = dataSource.GetLayer()
    ctranl = osr.CoordinateTransformation(linesLayer.GetSpatialRef(),targRef)
    
    interLines = []
    # Intersect of BUFFER and LINES
    for line in linesLayer:
        ingeom_line = line.GetGeometryRef()
        ingeom_line.Transform(ctranl)
        if ingeom_line.Intersect(geomBuffer):
            interLines.append((line,ingeom_line))
    # Split INTER_LINES based on points (INTER_SITES)
    resLines = []    
    for sentry in interSites:
        s_geom = sentry[1]
        for lentry in interLines:
            l_geom = lentry[1]
            if s_geom.Intersect(l_geom):
                # For testing reasons we will only add the resulting geometry to the list
                resLines.append(s_geom.Intersection(l_geom))
    
    # Navigate Network; Return Network ...
    print(resLines)
    
    # Display all in folium GeoJSON
    m = folium.Map(location=[y,x],zoom_start=13)
    folium.Marker([y,x],popup='<b>USER_CLICK</b>').add_to(m)
    targWebRef = osr.SpatialReference()
    targWebRef.ImportFromEPSG(4326)
    cTransf = osr.CoordinateTransformation(sl.GetSpatialRef(),targWebRef)

    for sentry in interSites:        
        s_geom = sentry[1] 
       # s_geom.Transform(cTransf)
        print("Adding marker to {0:.10f},{1:.10f}".format(s_geom.GetY(),s_geom.GetX()))
        folium.Marker([s_geom.GetY(),s_geom.GetX()],popup='<b>SITE</b>').add_to(m)

    display(m)


if __name__ == "__main__":
   isolateNetwork("Data\\GDAL_Data","SitesSnapped","NHDFlowline_Subset",-73.939645996,42.378012068)
