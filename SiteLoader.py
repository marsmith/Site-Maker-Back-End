import json


def SiteLoader(filepath):
    jsonDict = open(filepath,"r").read()
    fList = jsonDict["features"]
    siteList = []

    for geomObj in fList:
        coordList = geomObj['geometry']['coordinates']
        site_no = geomObj['properties']['site_no']
        temp = []
        temp.append(coordList)
        temp.append(site_no)
        siteList.append(temp)