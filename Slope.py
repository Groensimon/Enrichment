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

import arcpy
from __future__ import division
from osgeo import gdal


def heightToSlope(heightInput1, heightInput2, heightInput3, heightInput4, workspace):
    arcpy.MosaicToNewRaster_management((heightInput1,heightInput2,heightInput3,heightInput4), workspace, "/ahn2RARaster.tif", "RD_New.prj", "8_BIT_UNSIGNED", 1, 1, "", "")
    ahn2Slope = Slope("C:/thesisData/ahn2RARaster.tif", "DEGREE", "")
    ahn2Slope.save("C:/thesisData/ahn2Slope.tif")
    return ahn2Slope



def getSlopeProbability(inputRaster):
    inputRaster = heightToSlope(heightInput1, heightInput2, heightInput3, heightInput4, workspace)
    p = Reclassify(inputRaster, "VALUE", RemapRange([[0,10,0.6],[10,20,1.0],[20,30,0.4],[30,40,0.2],[40,90,0.0]]), "NODATA")
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
    heightInput1 = #Forgot my external harddrive with this data, will update asap
    heightInput2 =
    heightInput3 =
    heightInput4 =
    inputData = "C:/Users/Simon/Documents/GitHub/Enrichment/tracksubset.geojson"
    objects = "C:/thesisData/network/links_corr/links_corr.shp"
    pointRasterValue(inputRaster, inputData, objects)


main()




