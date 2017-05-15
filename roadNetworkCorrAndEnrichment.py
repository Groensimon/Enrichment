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
from arcpy import env


arcpy.env.overwriteOutput = True




def networkPreProcessing(objects):
    arcpy.Delete_management("C:/Users/Simon/Documents/GitHub/Enrichment/networkPr_update.shp")
    networkFL = arcpy.CopyFeatures_management(objects, "C:/Users/Simon/Documents/GitHub/Enrichment/networkUpdate")
    arcpy.MakeFeatureLayer_management(networkFL, "networkPr_update")
    expression = """("navigatie" = 'onderdeel van rotonde' OR "navigatie" = 'onderdeel van kruispunt' OR "wegtype" = 'bromfietspad (langs weg)' OR "wegtype" = 'fietspad (langs weg)' OR "wegtype" = 'fietsstraat' OR "wegtype" = 'solitair bromfietspad' OR "wegtype" = 'solitair fietspad' OR "wegtype" = 'voetgangersdoorsteekje' OR "wegtype" = 'voetgangersgebied' OR "wegtype" = 'weg met fiets(suggestie)strook' ) AND "verlichtin" = ' ' OR "verlichtin" = 'beperkt verlicht (bijvoorbeeld alleen bij kruispunten)' OR "verlichtin" = 'goed verlicht' OR "verlichtin" = 'niet verlicht' OR "verlichtin" = 'ONBEKEND'"""
    arcpy.SelectLayerByAttribute_management("networkPr_update", "NEW_SELECTION", expression)
    if int(arcpy.GetCount_management("networkPr_update").getOutput(0)) < 0:
        arcpy.DeleteRows_management("networkPr_update")
    updatedNetwork = arcpy.FeatureClassToShapefile_conversion("networkPr_update", "C:/Users/Simon/Documents/GitHub/Enrichment/")
    return updatedNetwork



def roadNetworkEnrich(objects):
    networkPreProcessing(objects)
    network = "C:/Users/Simon/Documents/GitHub/Enrichment/networkPr_update.shp"
    #Deleting all the fields that are generated in this definition to prevent errors.
    arcpy.DeleteField_management(network, ["lightQual", "roadType", "roadQual", "roadHindr", "surfQual"])
    #For the quality of street lighting.
    arcpy.AddField_management(network, "lightQual", "FLOAT", 4, 4, "", "", "NULLABLE")
    #The block of python code that allows a text variable to be reclassed into a float variable!
    expression1 = "Reclass(!verlichtin!, !lightQual!)"
    codeblock1 = """def Reclass(x, y):
        if (x == 'ONBEKEND' or x == 'niet verlicht'):
            y = 0.00
        elif (x == 'beperkt verlicht (bijvoorbeeld alleen bij kruispunten)'):
            y = 0.50
        elif (x == ' ' or x == 'goed verlicht'):
            y = 1.00
        return y"""
    arcpy.CalculateField_management(network, "lightQual", expression1, "PYTHON_9.3", codeblock1)

    #For the type of road surface.
    arcpy.AddField_management(network, "roadType", "FLOAT", 4, 4, "", "", "NULLABLE")
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
    arcpy.CalculateField_management(network, "roadType", expression1, "PYTHON_9.3", codeblock1)
    #For the quality of the surface.
    arcpy.AddField_management(network, "roadQual", "FLOAT", 4, 4, "", "", "NULLABLE")
    expression2 = "Reclass(!wegkwal!, !roadQual!)"
    codeblock2 = """def Reclass(x, y):
        if (x == 'ONBEKEND'):
            y = 0.50
        elif (x == 'slecht'):
            y = 0.00
        elif (x == 'redelijk'):
            y = 0.75
        elif (x == ' ' or x == 'goed'):
            y = 1.00
        return y"""
    arcpy.CalculateField_management(network, "roadQual", expression2, "PYTHON_9.3", codeblock2)
    #For the amount of hindrances on the surface.
    arcpy.AddField_management(network, "roadHindr", "FLOAT", 4, 4, "", "", "NULLABLE")
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
    arcpy.CalculateField_management(network, "roadHindr", expression3, "PYTHON_9.3", codeblock3)
    #Calculating the total surface quality score.
    arcpy.AddField_management(network, "surfQual", "FLOAT", 4, 4, "", "", "NULLABLE")
    expression4 = "([roadType] + [roadQual] + [roadHindr]) / 3.0000"
    arcpy.CalculateField_management(network, "surfQual", expression4)


def surfQualProbability(point, objects, decayConstantEu, maxdist=100):
    candidates = getCandidates(point, objects, decayConstantEu, maxdist=100)
    for candidate in candidates:
        p = ['surfQual']
        #print p
    return p


#objects = "C:/Users/3857611/Downloads/Enrichment-master/networkPr_corr.shp"
objects = "C:/Users/Simon/Documents/GitHub/Enrichment/networkPr_corr.shp"
roadNetworkEnrich(objects)