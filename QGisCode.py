import os
import math

'''
'''

from qgis import core as qcore
from PyQt4.QtCore import QVariant
R = 10000.0

def generateUserClickBuffer(x,y,geoSpatialRef=-1):
    ''' Will generate a user click buffer
    around the x,y location.
    '''
    if geoSpatialRef == -1:
        pass
    else:
        pass
    userClick = qcore.QgsPoint(x,y)
    
    
    outLayer = qcore.QgsVectorLayer("Polygon?crs=epsg:2829&field=id:integer",'USER_CLICK_BUFFER','memory')
    outLayer.startEditing()

    inGeom = qcore.QgsGeometry.fromPoint(userClick)

    bufferUC = inGeom.buffer(R,50) # Buffer to 10 km or 10,000 m
    print (math.pi * math.pow(R,2) - bufferUC.area())
    print "Wow"


    poly=bufferUC.asPolygon()
    outFeature = qcore.QgsFeature(outLayer.fields())

    print outFeature.setGeometry(qcore.QgsGeometry.fromPolygon(poly))
    print outFeature.setAttributes([1])
    
    print outLayer.addFeature(outFeature)
    outLayer.updateExtents()
    outLayer.endEditCommand()
    cntr = 0
    for feature in outLayer.getFeatures():
        cntr += 1
    print "Sucesfully Created buffer with radius:{0} and {1} features".format(R,cntr)
    _writer = qcore.QgsVectorFileWriter.writeAsVectorFormat(outLayer,"USER_CLICK_BUFFER.shp","utf-8",None,"ESRI Shapefile")

if __name__ == "__main__":
    generateUserClickBuffer(10,13,-1)