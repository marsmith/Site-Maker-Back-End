import arcpy

inFeature = arcpy.GetParameter(0)

for row in arcpy.da.SearchCursor(inFeature,["OID@","SHAPE@"]):
