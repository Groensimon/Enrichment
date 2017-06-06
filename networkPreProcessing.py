import arcpy
from arcpy import env
arcpy.env.overwriteOutput = True



def networkPreProcessing(bikeNetwork, footNetwork):
    arcpy.Delete_management("C:/Users/Simon/Documents/GitHub/Enrichment/networkPr_update.shp", "")
    bikeNetworkFL = arcpy.CopyFeatures_management(bikeNetwork, "C:/Users/Simon/Documents/GitHub/Enrichment/bikeNetworkUpdate")
    arcpy.MakeFeatureLayer_management(bikeNetworkFL, "bikeNetworkPr_update")
    expressionBike = """("navigatie" = 'onderdeel van rotonde' OR "navigatie" = 'onderdeel van kruispunt' OR "wegtype" = 'bromfietspad (langs weg)' OR "wegtype" = 'fietspad (langs weg)' OR "wegtype" = 'fietsstraat' OR "wegtype" = 'solitair bromfietspad' OR "wegtype" = 'solitair fietspad' OR "wegtype" = 'voetgangersdoorsteekje' OR "wegtype" = 'voetgangersgebied' OR "wegtype" = 'weg met fiets(suggestie)strook' ) AND "verlichtin" = ' ' OR "verlichtin" = 'beperkt verlicht (bijvoorbeeld alleen bij kruispunten)' OR "verlichtin" = 'goed verlicht' OR "verlichtin" = 'niet verlicht' OR "verlichtin" = 'ONBEKEND'"""
    arcpy.SelectLayerByAttribute_management("bikeNetworkPr_update", "NEW_SELECTION", expressionBike)
    if int(arcpy.GetCount_management("bikeNetworkPr_update").getOutput(0)) < 0:
        arcpy.DeleteRows_management("bikeNetworkPr_update")

    footNetworkFL = arcpy.CopyFeatures_management(footNetwork, "C:/Users/Simon/Documents/GitHub/Enrichment/footNetworkUpdate")
    arcpy.MakeFeatureLayer_management(footNetworkFL, "footNetworkPr_update")
    expressionFoot = """VERHARDINGSBREEDTEKLASSE = '< 2 meter' OR VERHARDINGSBREEDTEKLASSE = '2 - 4 meter' AND (TYPEWEG_1 = 'overig' AND (HOOFDVERKEERSGEBRUIK_1 = 'gemengd verkeer' OR HOOFDVERKEERSGEBRUIK_1 = 'voetgangers') AND (VERHARDINGSTYPE = 'half verhard' OR VERHARDINGSTYPE = 'onbekend' OR VERHARDINGSTYPE = 'onverhard'))"""
    arcpy.SelectLayerByAttribute_management("footNetworkPr_update", "NEW_SELECTION", expressionFoot)
    if int(arcpy.GetCount_management("footNetworkPr_update").getOutput(0)) < 0:
        arcpy.DeleteRows_management("footNetworkPr_update")

    updatedNetworkBike = arcpy.FeatureClassToShapefile_conversion("bikeNetworkPr_update", "C:/Users/Simon/Documents/GitHub/Enrichment/")
    updatedNetworkFoot = arcpy.FeatureClassToShapefile_conversion("footNetworkPr_update", "C:/Users/Simon/Documents/GitHub/Enrichment/")
    arcpy.Delete_management("C:/Users/Simon/Documents/GitHub/Enrichment/networkUpdate.shp", "C:/Users/Simon/Documents/GitHub/Enrichment/footNetworkUpdate.shp")
    return updatedNetwork



bikeNetwork = "C:/thesisData/2NetworkAndSurfaceQuality/network.gdb/..."
footNetwork = "C:/thesisData/2NetworkAndSurfaceQuality/network.gdb/WEGDEEL_HARTLIJN"
networkPreProcessing(bikeNetwork, footNetwork)
