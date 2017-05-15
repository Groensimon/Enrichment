#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Simon
#
# Created:     13-04-2017
# Copyright:   (c) Simon 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from __future__ import division
import arcpy
from arcpy.sa import *
#import gdal

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True



def heightToSlope(heightInput1, heightInput2, heightInput3, heightInput4, workspace, projectDataset):
    arcpy.Delete_management("C:/thesisData/ahn2RARaster.tif")
    arcpy.Delete_management("C:/thesisData/ahn2Slope.tif")
    arcpy.MosaicToNewRaster_management((heightInput1,heightInput2,heightInput3,heightInput4), workspace, "/ahn2RARaster.tif", projectDataset, "8_BIT_UNSIGNED", 0.5, 1, "", "")
    ahn2Slope = Slope("C:/thesisData/ahn2RARaster.tif", "DEGREE", "")
    ahn2Slope.save("C:/thesisData/ahn2Slope.tif")
    return ahn2Slope



def getSlopeProbability(heightInput1, heightInput2, heightInput3, heightInput4, workspace, projectDataset):
    inputRaster = heightToSlope(heightInput1, heightInput2, heightInput3, heightInput4, workspace, projectDataset)
    myRemapRange = RemapRange([[0.0000, 10.0000, 0.6], [10.0000, 20.0000, 1.0], [20.0000, 30.0000, 0.4], [30.0000, 40.0000, 0.2], [40.0000, 88.5361, 0.0]])
    p = Reclassify(inputRaster, "VALUE", myRemapRange, "NODATA")
    return p



def pointRasterValue(inputRaster, inputData, objects):
    getData = gdal.Open(getSlopeProbability(inputRaster))
    gt = gdata.GetGeoTransform()
    data = gdata.ReadAsArray().astype(np.float)
    gdata = None
    x,y = float(LoadFromGeoJSON(inputData, objects))
    return data[x,y]



def getTrackPoints(trackarray, objects):
    """
    Turns track shapefile into a list of point geometries, reprojecting to the planar RS of the network file
    """
    trackpoints = []
    for coordinates in trackarray:
        if type(coordinates).__name__ == 'list':
            print coordinates
            X = float(coordinates[0])
            Y = float(coordinates[1])
            point = arcpy.Point(X,Y)
            pointGeometry = arcpy.PointGeometry(point, (arcpy.SpatialReference(4326))).projectAs(arcpy.Describe(objects).spatialReference) #RD_New
            trackpoints.append(pointGeometry)
    return trackpoints



def LoadFromGeoJSON(inputData, objects):
    #Loading the EHV0.json file into the script
    with open(inputData) as json_data:
        data = json.load(json_data)

    #creating an empty list called 'tracks' and making data a global attribute
    tracks = []
    global data
    js = {}

    #Adding the _id and coordinates to the list 'tracks'
    number = 0
##    js["features"] = data["features"][0:5]
##    with open('tracksubset.geojson', 'w') as outfile:
##        json.dump(js, outfile)

    for track in data["features"]:
        ID = track["properties"]["runid"]
        Distance = track["properties"]["distance"]
        Duration = track["properties"]["duration"]
        #for j in data[0]["trail"]:
        coordinates = track["geometry"]["coordinates"]

        #for coordinate in coordinates:
        print coordinates
        trackpoints = getTrackPoints(coordinates, objects)
        tracks.append([ID,trackpoints])
        number += 1
        if number ==5:
            break
    #print tracks
    return tracks



def main():
    workspace = "C:/thesisData"
    heightInput1 = "C:/thesisData/AHN2/n51bz1.tif"
    heightInput2 = "C:/thesisData/AHN2/n51dn1.tif"
    heightInput3 = "C:/thesisData/AHN2/n51dn2.tif"
    heightInput4 = "C:/thesisData/AHN2/n51dz1.tif"
    inputData = "C:/Users/Simon/Documents/GitHub/Enrichment/tracksubset.geojson"
    objects = "C:/thesisData/network/links_corr/links_corr.shp"
    projectDataset = "C:/thesisData/researchArea/Noord_Brabant.prj"
    getSlopeProbability(heightInput1, heightInput2, heightInput3, heightInput4, workspace, projectDataset)
    #pointRasterValue(inputRaster, inputData, objects)


main()




