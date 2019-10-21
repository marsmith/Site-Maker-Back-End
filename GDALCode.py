from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from osgeo import gdal_array
from osgeo import gdalconst
import os
import json
import folium
from Precompiler import *


def geomToGeoJSON(in_geom, name, simplify_tolerance= None, in_ref = None, out_ref = None,outPath=None):
    '''
    Matry's Function! Converts Geometry to GeoJSON
    '''
    if not simplify_tolerance is None:
        in_geom = in_geom.Simplify(simplify_tolerance)
    transform = osr.CoordinateTransformation(in_ref, out_ref)      
    
    #don't want to affect original geometry
    transform_geom = in_geom.Clone()      

    #trasnsform geometry from whatever the local projection is to wgs84
    if in_ref is None or out_ref is None:
        pass
    else:
        transform_geom.Transform(transform)
        
    json_text = transform_geom.ExportToJson()
    #add some attributes

    geom_json = json.loads(json_text)
    #get area in local units

    area = in_geom.GetArea()
    
    geojson_dict = {

        "type": "Feature",

        "geometry": geom_json,

        "properties": {

            "area": area

        }

    }
    geojson = json.dumps(geojson_dict)
    if not outPath is None:

        f = open('./' + name + '.geojson','w')

        f.write(geojson)

        f.close()

        print('Exported geojson:', name)       

    return geojson

class Node(object):
    def __init__(self,ownGeometry,edge1,edge2):
        self.geom = ownGeometry
        self.edge1 = edge1
        self.edge2 = edge2
    

    
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
    targRef.ImportFromEPSG(26918) # NY State Projection; consider a check from the provided site dataset instead
    
    # Create point from x,y and targRef
    ctran = osr.CoordinateTransformation(oRef,targRef)
    [p_lng,p_lat,z] = ctran.TransformPoint(x,y)
    inputPointProj = ogr.Geometry(ogr.wkbPoint)
    inputPointProj.SetPoint_2D(0,p_lng,p_lat)


    print("I got to here")

    geomBuffer = inputPointProj.Buffer(10000) # Buffer 10 km around the geometry
 
    # Load Selected Sites
    sitesDataSource = ogr.Open(path_sites)
    sl = sitesDataSource.GetLayer()
    ctran = osr.CoordinateTransformation(sl.GetSpatialRef(),targRef)
    
    # Intersect of BUFFER and SITES
    interSites = []
    for site in sl:
        ingeom_site = site.GetGeometryRef()
        if ingeom_site.Intersect(geomBuffer):
            # This site is inside the buffer!
            interSites.append((site,ingeom_site.Buffer(1)))
    print("There are {0} sites inside the ring!".format(len(interSites)))
    # Load Selected Lines
    dataSource = ogr.Open(path)
    shpdriver = ogr.GetDriverByName('ESRI Shapefile')
    linesLayer = dataSource.GetLayer()
    
    linesLayer.SetSpatialFilter(geomBuffer)
    
    # Get certain info about line attributes
    lineName_index = linesLayer.GetLayerDefn().GetFieldIndex("GNIS_NAME")
    lineRC_index = linesLayer.GetLayerDefn().GetFieldIndex("ReachCode")
    lineLength_index = linesLayer.GetLayerDefn().GetFieldIndex("LengthKM")
    lineID_index = linesLayer.GetLayerDefn().GetFieldIndex("GNIS_ID")
    lineFCode_index = linesLayer.GetLayerDefn().GetFieldIndex("FCode")
    # 46000 - 46007 StreamRiver [OK]
    # 55800 ArtificialPath [OK]
    # 56600 Coastline [only on coast. Do NOT use if not connected to an NHD Waterbody
    # that is also a lake]
    # 33400 Connector [OK]
    
    # Get certain info about site attributes
    siteNumber_index = sl.GetLayerDefn().GetFieldIndex("site_no")
    stationName_index = sl.GetLayerDefn().GetFieldIndex("station_nm")
    
    siteCounter = 0
    
    
    interLines = []
    # Intersect of BUFFER and LINES
    for line in linesLayer:        
        interLines.append(line)
    print(len(interLines))    
      
    # Buffer all Lines
    lBufferStore = {} # Stores line entry, Bool flag)
    
    sitesStore = {}# Stores Site object (fake site)
    flowlineList = [] # Stores Flowline object (flow)
    
    
    # Create Buffer polygon where user clicked    
    # Find line which ucBuff intersects
    ucBuff = inputPointProj.Buffer(1)
    i = 0
    startingIndex = None
    for line in interLines:       
        e = (line.GetGeometryRef().Buffer(1),False)
        lBufferStore[line] = e[1] # Original Line, Buffered Geometry 
        if ucBuff.Intersects(e[0]):
            startingLine = line
            print("I will start at line index {0}".format(startingIndex))
        i += 1
        
    if startingLine is None:
        print("ERROR: USER_CLICK does not intersect any existing lines")
        return
    
    queue.append(startingLine)
    
    queue = [] # Stores keys
    while len(queue) > 0:
        e = queue.pop(0) # This will be the line
        if lBufferStore[e] == True:
            # We have already visited this
            continue
        else:
            _npt = e.GetPointCount()
            upPt = e.GetPoint(0)
            upBuff = upPt.Buffer(1)
            downPt = e.GetPoint(_npt - 1)
            downBuff = downPt.Buffer(1)
            # See if any of the sites are also that endpoint
            b_f = [False,False]
            upSite = None
            downSite = None
            
            # Check if any real sites exist at the endpoint
            for s in interSites:
                s_geom = s.GetGeometryRef().Buffer(1)
                if s_geom.Intersects(upPt):
                    # Found existing upper extent
                    b_f[0] = True
                    foundExistingSiteGeom = False
                    for k,v in sitesStore.items():
                        if k.Intersects(s_geom):
                            # Use the existing entry as site
                            foundExistingSiteGeom = True
                            upSite = sitesStore[k]                            
                            
                    if not foundExistingSiteGeom:
                        # Need to create our own an add it to the table
                        sid = SiteID(s.GetFieldAsString(siteNumber_index))
                        s = Site(sid,s_geom.GetX(),s_geom.GetY())
                        sitesStore[s_geom] = s
                        upSite = s
                        
                elif s_geom.Intersects(downPt):
                    # Found existing lower extent
                    b_f[1] = True
                    foundExistingSiteGeom = False
                    for k,v in sitesStore.items():
                        if k.Intersects(s_geom):
                            # Use the existing entry as site
                            foundExistingSiteGeom = True
                            downSite = sitesStore[k]                            
                            
                    if not foundExistingSiteGeom:
                        # Need to create our own an add it to the table
                        sid = SiteID(s.GetFieldAsString(siteNumber_index))
                        s = Site(sid,s_geom.GetX(),s_geom.GetY())
                        sitesStore[s_geom] = s
                        downSite = s
                 
                
            # Find out which lines intersect on that point
            for k,v in lBufferStore.items():
                if k == e:
                    continue
                else:
                    k_geom = k.GetGeometryRef()
                    if k_geom.Intersects(upBuff) and not b_f[0]:
                        # Found an upstream flowline
                        queue.append(k)
                    elif k_geom.Intersects(downBuff) and not b_f[1]:
                        # Found a downstream flowline
                        queue.append(k)
            # Declare we have now visited and added this line
            lBufferStore[e] = True
            # Say our flowline has connections to each node, then,
            
            # If no real sites intersect at this point, maybe there are fake
            # ones which do already
            if upSite is None:
                # Try and find site in existing table or create it
                foundExisting = False
                for k,v in sitesStore.items():                    
                    if k.Intersects(upPt):
                        foundExisting = True
                        upSite = sitesStore[k]
                if not foundExisting:
                    s = Site(siteCounter,upPt.GetX(),upPt.GetY())
                    sitesStore[upPt.Buffer(1)] = s
                    upSite = s
                    siteCounter += 1
                
            if downSite is None:
                # Try and find site in existing table or create it
                foundExisting = False
                for k,v in sitesStore.items():
                    if k.Intersects(downPt):
                        foundExisting = True
                        downSite = sitesStore[k]
                if not foundExisting:
                    s = Site(siteCounter,downPt.GetX(),downPt.GetY())
                    downSite = s
                    sitesStore[downPt.Buffer(1)] = s
                    siteCounter += 1
                    
            fid = e.GetFieldAsString(lineID_index)
            flen = float(e.GetFieldAsString(lineLength_index))
            fName = e.GetFieldAsString(lineName_index)
            fCode = e.GetFieldAsString(lineFCode_index)
            fRC = int(e.GetFieldAsString(lineRC_index)) # Go 1676!!
            
            f = Flowline(fid,upSite,downSite,flen,fRC)
            # Line has been constructed, add to the table
            upSite.flowsCon.append(f)
            downSite.flowsCon.append(f)
    
            
    return
        
    # Store which ones intersect which other ones
    
    # Create Node objects at the difference of the intersections
    # Flag nodes which share Intersection with existing sites
    
    # Derive Network Relationship

    # Display all in folium GeoJSON
    m = folium.Map(location=[y,x],zoom_start=13)
    folium.Marker([y,x],popup='<b>USER_CLICK</b>').add_to(m)
    
    for i in range(len(interSites)):
        sentry = interSites[i]
        geoJ = geomToGeoJSON(sentry[1],"",10,sl.GetSpatialRef(),oRef)
        if i == 12:
            print(geoJ)
        folium.GeoJson(data=geoJ).add_to(m)  
    
    # Draw all the interLines onto the folium map
    for lentry in interLines:
        
        geoJ = geomToGeoJSON(lentry.GetGeometryRef(),"",10,linesLayer.GetSpatialRef(),oRef)
        folium.GeoJson(data=geoJ).add_to(m)    
    
    display(m)
    
