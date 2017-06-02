import json
import arcpy
from arcpy.sa import *
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("spatial")



def LoadFromGeoJSON(inputData, objects):
    global data
    #Loading the EHV0.json file into the script
    with open(inputData) as json_data:
        data = json.load(json_data)
    #creating an empty list called 'tracks' and making data a global attribute
    tracks = []
    number = 0
    for track in data["features"]:
        coordinates = track["geometry"]["coordinates"]
        ID = track["properties"]["runid"]
        Distance = track["properties"]["distance"]
        Duration = track["properties"]["duration"]
        trackpoints = coordinates
        tracks.append([trackpoints, ID, Distance, Duration])
        number += 1
        if number ==5:
            break
    #print tracks
    return tracks



def toSHP(inputData, objects, workspace, fcname):
    try:
        if arcpy.Exists("E:/Simon_Thesis/geojson.shp"):
            arcpy.Delete_management("E:/Simon_Thesis/geojson.shp")
    except arcpy.ExecuteError:
            arcpy.AddError(arcpy.GetMessages(2))
    except:
            e=sys.exc_info()[1]
            print (e.args[0])
    #Creating an empty feature class, adding the necessary attributes for id and the coordinates and reading the data in
    tracks = LoadFromGeoJSON(inputData, objects)
    runnerTracks = arcpy.CreateFeatureclass_management(workspace,fcname,"POINT",'','','',4326)
    arcpy.AddField_management(runnerTracks,"RID","TEXT")
    arcpy.AddField_management(runnerTracks,"Distance","FLOAT")
    arcpy.AddField_management(runnerTracks,"Duration","FLOAT")
    with arcpy.da.InsertCursor(runnerTracks,["SHAPE@XY","RID","Distance","Duration"]) as cur:
        for track in tracks:
            ID = track[1]
            Distance = track[2]
            Duration = track[3]
            for coordinates in track[0]:
                try:
                    X = float(coordinates[0])
                    Y = float(coordinates[1])
                except ValueError,e:
                    print "error",e,"on line",trackpoints
                point = arcpy.Point(X,Y)
                pointGeometry = arcpy.PointGeometry(point, arcpy.SpatialReference(4326))
                row = (pointGeometry,ID,Distance,Duration)
                cur.insertRow(row)
            print row
    runnerTracksRD = arcpy.Project_management(runnerTracks, "E:/Simon_Thesis/geojsonRD.shp", 28992, "Amersfoort_To_WGS_1984_NTv2") #28992 is the authority code for RD_New!!
    return runnerTracksRD




"""
Road network segments
"""

def getTrackPoints(tracks, objects):
    """
    Turns track shapefile into a list of point geometries, reprojecting to the planar RS of the network file
    """
    trackpoints = []
    for coordinates in tracks:
        if type(coordinates).__name__ == 'list':
            #print coordinates
            X = float(coordinates[0])
            Y = float(coordinates[1])
            point = arcpy.Point(X,Y)
            pointGeometry = arcpy.PointGeometry(point, (arcpy.SpatialReference(4326))).projectAs(arcpy.Describe(objects).spatialReference) #RD_New
            trackpoints.append(pointGeometry)
    return trackpoints



def airQualityIntersect(inputData, objects, workspace, fcname):
    points = toSHP(inputData, objects, workspace, fcname)
    airQualityRaster = "E:/Simon_Thesis/recalculatedRasters/airpol_tot"
    ExtractValuesToPoints(points, airQualityRaster, "E:/Simon_Thesis/recalculatedRasters/airQualityTracks.shp", "INTERPOLATE", "VALUE_ONLY")



workspace = "E:/Simon_Thesis/"
fcname = "geojson.shp"
objects = "E:/Simon_Thesis/networkPr_update.shp"
inputData = "E:/Simon_Thesis/EHV-clean.geojson"
#tracks = LoadFromGeoJSON(inputData, objects)
#getTrackPoints(tracks, objects)
#toSHP(inputData, objects, workspace, fcname)
airQualityIntersect(inputData, objects, workspace, fcname)
