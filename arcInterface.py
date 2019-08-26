'''
python 2.7.13
arcInterface -- Set of basic functions to interact with arcGIS

'''
import arcpy
import io
import shutil

dPath = r"C:\\Users\\mpanozzo\\Downloads\\nhd_ny\\"
theRoad_class = r"C:\\Users\\mpanozzo\\Downloads\\nhd_ny\\CustomData.gdb\\theRoad"

'''
createFeature(name,typeT,out,overwrite): Will create a shapefile for
a feature such as points. Takes in name of input and type of input (ex "POINT")
Outputs to out.
'''
def createFeature(name,typeT,out = theRoad_class,overwrite = False):    
    # Set local variables
    # USE CODE 4269 if you cannot get a spatial_ref
    name = name + ".shp"
    # Check if exists already.
    try:
        with io.open(name) as file:
            file.close()
        if overwrite:            
            # We should delete
            shutil.rmtree(name)
        else:
            return
    except:
        pass # File is not there, create as normal
        

    template = "NY_sitefile.shp"
    has_m = "DISABLED"
    has_z = "DISABLED"
    # TODO: Add the 'NAME' field for the newly created feature class
    # Use Describe to get a SpatialReference object
    spatial_ref = arcpy.Describe(dPath + template).spatialReference    
    # Execute CreateFeatureclass
    result = arcpy.management.CreateFeatureclass(dPath,name,typeT,dPath + template,has_m,has_z,spatial_ref)
    feature_class = result[0]
'''
obtain_vertices(originalFile): Will obtain the vertices on a polyline
Returns a list of arcGIS Point objects
'''
def obtain_vertices(originalFile):
    pointList = []
    with arcpy.da.SearchCursor(originalFile,['SHAPE@']) as s_cur:
        for row in s_cur:
            polyline = row[0]
            for feature in polyline:
                for point in feature:
                    print point
                    pointList.append(point)
    return pointList

def filter_toGraphNodes(points):
    pl = []
    return pl

''' Note to self: ADD attributes after the SHAPE@
'''
def putInFeature(name,typeT,points):
    name = name + ".shp"
    fullP = dPath + name
    with arcpy.da.InsertCursor(fullP,['SHAPE@']) as curs:
        for i in range(0,len(points)):
            # ROW[  CURSOR OBJ( NAME,   SHAPE)        ]
            curs.insertRow([points[i]])
    # Done inserting!


if __name__ == "__main__":  

    createFeature("theRoad_INTERSECT","POINT")  
    pointList = obtain_vertices(theRoad_class)
    goodPoints = filter_toGraphNodes(pointList)
    putInFeature('theRoad_INTERSECT',"POINT",pointList)
    print "HI"
    
