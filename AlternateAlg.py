import arcpy


DATA_PATH = "C:/Users/mpanozzo/Documents/ArcGIS/Projects/AddonisTest/AddonisTest.gdb/"

def isolateFlowline(reachCode):
    # Step 1: Find the flowline in NHD based on reachCode
    exp = "ReachCode='" + reachCode + "'"

    feature = arcpy.Select_analysis(DATA_PATH + "NHD_FlowlineReduced",DATA_PATH + "NHD_Select",exp)
    return feature

def createConnectedJSON(feature):
    pass


if __name__ == "__main__":
    f = isolateFlowline("02020008001891")
    print(f)