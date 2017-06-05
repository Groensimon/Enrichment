#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Simon
#
# Created:     20-03-2017
# Copyright:   (c) Simon 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

"""
Get together 3 examples of enrichment for the tracks with this script!!
"""



import arcpy
from math import exp, sqrt
import json
import sys
arcpy.CheckOutExtension("spatial")
from arcpy import env

arcpy.env.overwriteOutput = True
arcpy.env.workspace = "C:/thesisData"



"""
Data loading and conversion to shapefile
"""

#A definition that converts a (geo)json file to a feature class that can be used for mapmatching
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
        #print coordinates
        trackpoints = getTrackPoints(coordinates, objects)
        tracks.append([ID,trackpoints])
        number += 1
        if number ==5:
            break
    #print tracks

    return tracks

def toSHP(tracks,workspace,fcname):
    try:
        if arcpy.Exists(fcname):
            arcpy.Delete_management(fcname)
    except arcpy.ExecuteError:
            arcpy.AddError(arcpy.GetMessages(2))
    except:
            e=sys.exc_info()[1]
            print (e.args[0])
    #Creating an empty feature class, adding the necessary attributes for id and the coordinates and reading the data in

    runnerTracks = arcpy.CreateFeatureclass_management(workspace,fcname,"POINT",'','','',4326)
    arcpy.AddField_management(runnerTracks,"RID","TEXT")
    with arcpy.da.InsertCursor(runnerTracks,["RID","SHAPE@XY"]) as cur:
        for track in tracks:
            ID = track[0]
            for coordinates in track[1]:
                X = float(coordinates[0])
                Y = float(coordinates[1])
                point = arcpy.Point(X,Y)
                pointGeometry = arcpy.PointGeometry(point, arcpy.SpatialReference(4326))
                row = (ID,pointGeometry)
                cur.insertRow(row)
            print row



"""
Road network segments
"""

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

def getPDProbability(dist, decayconstant = 10):
    """
    The probability that given a certain distance between points and segments, the point is on the segment
    This needs to be parameterized
    Turn difference into a probability with exponential decay function
    """
    decayconstant= float(decayconstant)
    dist = float(dist)
    try:
        p = 1 if dist == 0 else round(1/exp(dist/decayconstant),4)
    except OverflowError:
        p =  round(1/float('inf'),2)
    return p

def getCandidates(point, objects, decayConstantEu, maxdist=100):
    """
    Returns closest segment candidates with a-priori probabilities.
    Based on maximal spatial distance of segments from point.
    """
    #point = tracks
    p = point.firstPoint #get the coordinates of the point geometry
    #print "Neighbors of point "+str(p.X) +' '+ str(p.Y)+" : "
    #Select all segments within max distance
    arcpy.Delete_management('objects_lyr')
    arcpy.MakeFeatureLayer_management(objects, 'objects_lyr')
    arcpy.SelectLayerByLocation_management ("objects_lyr", "WITHIN_A_DISTANCE", point, maxdist)
    candidates = {}
    #Go through these, compute distances, probabilities and store them as candidates
    cursor = arcpy.da.SearchCursor('objects_lyr', ["id", "SHAPE@"])
    row =[]
    for row in cursor:
        #compute the spatial distance
        dist = point.distanceTo(row[1])
        #compute the corresponding probability
        candidates[row[0]] = getPDProbability(dist, decayConstantEu)
    del row
    del cursor
    print str(candidates)
    return candidates




"""
Surface quality and street lighting

Added this definition which adds surface quality and the quality of street lighting to the road network (might need to split those into two separate definitions down the line)
"""

def networkPreProcessing(objects):
    arcpy.Delete_management("C:/Users/Simon/Documents/GitHub/Enrichment/networkPr_update.shp")
    networkFL = arcpy.CopyFeatures_management(objects, "C:/Users/Simon/Documents/GitHub/Enrichment/networkUpdate")
    arcpy.MakeFeatureLayer_management(networkFL, "networkPr_update")
    expression = """("navigatie" = 'onderdeel van rotonde' OR "navigatie" = 'onderdeel van kruispunt' OR "wegtype" = 'bromfietspad (langs weg)' OR "wegtype" = 'fietspad (langs weg)' OR "wegtype" = 'fietsstraat' OR "wegtype" = 'solitair bromfietspad' OR "wegtype" = 'solitair fietspad' OR "wegtype" = 'voetgangersdoorsteekje' OR "wegtype" = 'voetgangersgebied' OR "wegtype" = 'weg met fiets(suggestie)strook' ) AND "verlichtin" = ' ' OR "verlichtin" = 'beperkt verlicht (bijvoorbeeld alleen bij kruispunten)' OR "verlichtin" = 'goed verlicht' OR "verlichtin" = 'niet verlicht' OR "verlichtin" = 'ONBEKEND'"""
    arcpy.SelectLayerByAttribute_management("networkPr_update", "NEW_SELECTION", expression)
    if int(arcpy.GetCount_management("networkPr_update").getOutput(0)) < 0:
        arcpy.DeleteRows_management("networkPr_update")
    updatedNetwork = arcpy.FeatureClassToShapefile_conversion("networkPr_update", "C:/Users/Simon/Documents/GitHub/Enrichment/")
    arcpy.Delete_management("C:/Users/Simon/Documents/GitHub/Enrichment/networkUpdate.shp")
    return updatedNetwork

def roadNetworkEnrich(objects):
    #preProcessing(objects)
    #network = "C:/Users/Simon/Documents/GitHub/Enrichment/networkPr_update.shp"
    #Deleting all the fields that are generated in this definition to prevent errors.
    arcpy.DeleteField_management(objects, ["lightQual", "roadType", "roadQual", "roadHindr", "surfQual"])
    #For the quality of street lighting.
    arcpy.AddField_management(objects, "lightQual", "FLOAT", 4, 4, "", "", "NULLABLE")
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
    arcpy.CalculateField_management(objects, "lightQual", expression1, "PYTHON_9.3", codeblock1)

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
        if (x == 'ONBEKEND'):
            y = 0.50
        elif (x == 'slecht'):
            y = 0.00
        elif (x == 'redelijk'):
            y = 0.75
        elif (x == ' ' or x == 'goed'):
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

def surfQualblaProbability(point,objects, decayConstantEu, maxDist=100):
    """
    candidates = getCandidates(points[0],objects, decayConstantEu, maxDist)
    for candidate in candidates:
        p = getattr(objects, "surfQual")
        #print p
        return p
    """
    candidates = getCandidates(points[0],objects, decayConstantEu, maxDist)
    #print candidates
    for candidate in candidates:

        probability = {}
        #Go through these, compute distances, probabilities and store them as candidates
        cursor = arcpy.da.SearchCursor(objects, ['id', 'surfQual'])
        row =[]
        for row in cursor:
            value = row[1]
            #compute the corresponding probability
            probability[row[0]] = round(value, 4)
        del row
        del cursor
        print str(probability)
        #print distances
        return probability


def surfQualProbability(tracks, workspace, fcname, objects, maxDist=100):
    """
    candidates = getCandidates(points[0],objects, decayConstantEu, maxDist)
    for candidate in candidates:
        p = getattr(objects, "surfQual")
        #print p
        return p
    """
    point = toSHP(tracks, workspace, fcname)
    p = point.firstPoint #get the coordinates of the point geometry
    #Select all segments within max distance
    arcpy.Delete_management('surface_lyr')
    arcpy.MakeFeatureLayer_management(objects, 'surface_lyr')
    arcpy.SelectLayerByLocation_management ("surface_lyr", "WITHIN_A_DISTANCE", point, maxdist)

    probability = {}
    #Go through these, compute distances, probabilities and store them as candidates
    cursor = arcpy.da.SearchCursor('surface_lyr', ['id', 'surfQual'])
    row =[]
    for row in cursor:
        value = row[1]
        #compute the corresponding probability
        probability[row[0]] = round(value, 4)
    del row
    del cursor
    print str(probability)
    #print distances
    return probability



"""
Natural areas
"""

def natureToFC(natureInput, clipInput):
    try:
        if arcpy.Exists("natureBrabant.shp"):
            arcpy.Delete_management("natureBrabant.shp")
        if arcpy.Exists("bbg2010FL_lyr"):
            arcpy.Delete_management("bbg2010FL_lyr")
        if arcpy.Exists("bbgFeatureLayer"):
            arcpy.Delete_management("bbgFeatureLayer")
    except arcpy.ExecuteError:
            arcpy.AddError(arcpy.GetMessages(2))
    except:
            e=sys.exc_info()[1]
            print (e.args[0])
    arcpy.Clip_analysis(natureInput, clipInput, "natureBrabant.shp", "")
    nature = arcpy.MakeFeatureLayer_management("natureBrabant.shp", "bbg2010FL_lyr", "BG2010A = 40 OR BG2010A = 43 OR BG2010A = 60 OR BG2010A = 61 OR BG2010A = 62")
    #arcpy.SelectLayerByAttribute_management("bbg2010FL_lyr", "NEW_SELECTION", "BG2010A = 40 OR BG2010A = 43 OR BG2010A = 60 OR BG2010A = 61 OR BG2010A = 62")
    #arcpy.CopyFeatures_management("bbg2010FL_lyr", "bbgFeatureLayer")
    return nature


def distToPolygon(point, objects, natureInput, clipInput, maxDist):
    """
    A defenition that should return the distance between each point and the nearest polygon
    """
    """
    polygon = natureToInfluenceRaster(natureInput, clipInput)
    point = getTrackPoints(trackarray, objects)
    nearestDist = arcpy.Near_analysis(points, polygon)
    #nearestDist = points.distanceTo(polygon.geometry[0])
    print nearestDist
    return nearestDist
    """
    #p = LoadFromGeoJSON(inputData, objects)
    p = point.firstPoint #get the coordinates of the point geometry
    #print "Neighbors of point "+str(p.X) +' '+ str(p.Y)+" : "
    #Select all segments within max distance
    #arcpy.Delete_management('')
    #arcpy.MakeFeatureLayer_management(objects, 'objects_lyr')
    arcpy.SelectLayerByLocation_management(natureToFC(natureInput, clipInput), "WITHIN_A_DISTANCE", p, 100)
    probabilities = {}
    #Go through these, compute distances, probabilities and store them as candidates
    cursor = arcpy.da.SearchCursor("bbg2010FL_lyr", ["FID", "SHAPE@"])
    row =[]
    for row in cursor:
        #compute the spatial distance
        dist = point.distanceTo(row[1])
        #compute the corresponding probability
        probabilities[row[0]] = getNatPB(dist, maxDist)
    del row
    del cursor
    print str(probabilities)
    #print distances
    return probabilities

def getNatPB(dist, maxDist): #Check if dist can actually be used for this, as it is also used for the network distance in a previous definition
    """
    A definition that should return the influence probability on a track point based on the distance between the point and the nearest polygon
    """
    #natureIR = natureToInfluenceRaster(natureInput, clipInput)
    dist = float(dist)
    #Function that returns a p between 1 and 0 based on a continues decay between 1 and 100 meter
    #try:
        #p = 1 if dist == 0 else round((1-(dist/maxDist)),4)
    #except dist >= 100:
        #p = 0
        #p =  round(1/float('inf'),2)
    if dist == 0:
        p = 1
    elif dist <= 100:
        p = round((1-(dist/maxDist)), 4)
    elif dist > 100:
        p = 0
    return p
    print p



"""
Enrichment
"""

def enrich(tracks, workspace, fcname, objects, decayConstantEu, maxDist, natureInput, clipInput):
    #track is a list of point geometries
    roadNetworkEnrich(objects)
    #natDistances = distToPolygon(inputData, objects, natureInput, clipInput, maxDist)
    #print natDistances
    candidates = getCandidates(tracks[0],objects, decayConstantEu, maxDist)
    print candidates
    surfaceQuality = surfQualProbability(tracks, workspace, fcname, objects, maxDist)
    print surfaceQuality

def iterateTracks(tracks, workspace, fcname, objects, decayConstantEu, maxDist, natureInput, clipInput):
    for track in tracks:
        ID = track[0]
        trackpoints = track[1]
        enrich(tracks, workspace, fcname, objects, decayConstantEu, maxDist, natureInput, clipInput)


"""
Setting the input parameters
"""

workspace = "C:/Users/Simon/Documents/GitHub/Enrichment/"
inputData = "C:/Users/Simon/Documents/GitHub/Enrichment/tracksubset.geojson"
fcname = "testRunnerTracks.shp"
#objects = "C:/thesisData/network/links_corr/links_corr.shp"
objects = "C:/Users/Simon/Documents/GitHub/Enrichment/networkPr_update.shp"
natureInput ="C:/thesisData/bodemstatistiek/bbg2010.shp"
clipInput = "C:/thesisData/researchArea/Noord_Brabant.shp"
maxDist = 100
tracks = LoadFromGeoJSON(inputData,objects)
#iterateTracks(tracks,objects,50,maxDist)
iterateTracks(tracks, workspace, fcname, objects, 50, maxDist, natureInput, clipInput)