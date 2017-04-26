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
    p = Reclassify(inputRaster, "VALUE", RemapRange([[0.0000, 10.0000, 0.6], [10.0000, 20.0000, 1.0], [20.0000, 30.0000, 0.4], [30.0000, 40.0000, 0.2], [40.0000, 88.5361, 0.0]]), "NODATA")
    return p



def pointRasterValue(inputRaster, inputData, objects):
    getData = gdal.Open(getSlopeProbability(inputRaster))
    gt = gdata.GetGeoTransform()
    data = gdata.ReadAsArray().astype(np.float)
    gdata = None
    x,y = float(LoadFromGeoJSON(inputData, objects))
    return data[x,y]



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




