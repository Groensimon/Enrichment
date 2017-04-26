#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Simon
#
# Created:     20-04-2017
# Copyright:   (c) Simon 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy


def surfaceQuality(objects):
    arcpy.DeleteField_management(objects, ["wegdekVal", "wegdeksrt2"])
    arcpy.AddField_management(objects, "wegdeksrt2", "Long", 30, "", 30, "", "NULLABLE")
    arcpy.CalculateField_management(objects, "wegdeksrt2", "wegdeksrt")
    arcpy.AddField_management(objects, "wegdekVal", "FLOAT", 3, 2, "", "", "NULLABLE")
    expression = "Reclass(!wegdeksrt2!)"
    codeblock = """def Reclass(x):
        if (x == ' ' or x == 'asfalt/beton'):
            return 0.01
        elif (x == 'klinkers' or x == 'ONBEKEND' or x == 'tegels'):
            return 0.33
        elif (x == 'halfverhard' or x == 'overig(hout/kinderkopjes e.d.)'):
            return 0.67
        elif (x == 'onverhard' or x == 'schelpenpad'):
            return 1.00"""
    arcpy.CalculateField_management(objects, "wegdekVal", expression, "PYTHON_9.3", codeblock)
    #arcpy.CalculateField_management(objects, "wegdekValue", ["' ' = -1.0 AND 'asfalt/beton' = -1.0 AND 'halfverhard' = 0.5 AND 'klinkers' = -0.5 AND 'ONBEKEND' = -0.5 AND 'onverhard' = 1 AND 'overig(hout/kinderkopjes e.d.)' = 0.5 AND 'schelpenpad' = 1 AND 'tegels' = -0.5 "])




objects = "C:/Users/Simon/Documents/GitHub/Enrichment/networkPr_corr.shp"
surfaceQuality(objects)