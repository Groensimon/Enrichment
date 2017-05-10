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
    #Deleting all the fields that are generated in this definition to prevent errors.
    arcpy.DeleteField_management(objects, ["roadType", "roadQual", "roadHindr", "surfQual"])
    #For the type of road surface.
    arcpy.AddField_management(objects, "roadType", "FLOAT", 4, 4, "", "", "NULLABLE")
    #The block of python code that allows a text variable to be reclassed into a float variable!
    expression1 = "Reclass(!wegdeksrt!, !roadType!)"
    codeblock1 = """def Reclass(x, y):
        if (x == ' ' or x == 'asfalt/beton'):
            y = 0.00
        elif (x == 'klinkers' or x == 'ONBEKEND' or x == 'tegels'):
            y = 0.33
        elif (x == 'halfverhard' or x == 'overig(hout/kinderkopjes e.d.)'):
            y = 0.67
        elif (x == 'onverhard' or x == 'schelpenpad'):
            y = 1.00
        return y"""
    arcpy.CalculateField_management(objects, "roadType", expression1, "PYTHON_9.3", codeblock1)
    #For the quality of the surface.
    arcpy.AddField_management(objects, "roadQual", "FLOAT", 4, 4, "", "", "NULLABLE")
    expression2 = "Reclass(!wegkwal!, !roadQual!)"
    codeblock2 = """def Reclass(x, y):
        if (x == ' ' or x == 'ONBEKEND'):
            y = 0.50
        elif (x == 'slecht'):
            y = 0.00
        elif (x == 'redelijk'):
            y = 0.75
        elif (x == 'goed'):
            y = 1.00
        return y"""
    arcpy.CalculateField_management(objects, "roadQual", expression2, "PYTHON_9.3", codeblock2)
    #For the amount of hindrances on the surface.
    arcpy.AddField_management(objects, "roadHindr", "FLOAT", 4, 4, "", "", "NULLABLE")
    expression3 = "Reclass(!hinder!, !roadHindr!)"
    codeblock3 = """def Reclass(x, y):
        if (x == ' ' or x == 'ONBEKEND'):
            y = 0.50
        elif (x == 'zeer veel'):
            y = 0.00
        elif (x == 'veel'):
            y = 0.25
        elif (x == 'redelijk'):
            y = 0.50
        elif (x == 'weinig'):
            y = 0.75
        elif (x == 'zeer weinig'):
            y = 1.00
        return y"""
    arcpy.CalculateField_management(objects, "roadHindr", expression3, "PYTHON_9.3", codeblock3)
    #Calculating the total surface quality score.
    arcpy.AddField_management(objects, "surfQual", "FLOAT", 4, 4, "", "", "NULLABLE")
    expression4 = "([roadType] + [roadQual] + [roadHindr]) / 3.0000"
    arcpy.CalculateField_management(objects, "surfQual", expression4)




objects = "C:/Users/3857611/Downloads/Enrichment-master/networkPr_corr.shp"
#objects = "C:/Users/Simon/Documents/GitHub/Enrichment/networkPr_corr.shp"
surfaceQuality(objects)
