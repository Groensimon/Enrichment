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


def streetLighting(objects):
    #Deleting all the fields that are generated in this definition to prevent errors.
    arcpy.DeleteField_management(objects, ["lightQual"])
    #For the quality of the street lighting
    arcpy.AddField_management(objects, "lightQual", "FLOAT", 4, 4, "", "", "NULLABLE")
    #The block of python code that allows a text variable to be reclassed into a float variable!
    expression1 = "Reclass(!verlichtin!, !lightQual!)"
    codeblock1 = """def Reclass(x, y):
        if (x == ' ' or x == 'ONBEKEND' or x == 'niet verlicht'):
            y = 0.00
        elif (x == 'beperkt verlicht (bijvoorbeeld alleen bij kruispunten)'):
            y = 0.50
        elif (x == 'goed verlicht'):
            y = 1.00
        return y"""
    arcpy.CalculateField_management(objects, "lightQual", expression1, "PYTHON_9.3", codeblock1)




#objects = "C:/thesisData/network/links_corr/links_corr.shp"
objects = "C:/Users/Simon/Documents/GitHub/Enrichment/networkPr_corr.shp"
streetLighting(objects)

