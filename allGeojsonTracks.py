import arcpy
from math import exp, sqrt
import json
import sys
arcpy.CheckOutExtension("spatial")



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
        #if number ==5:
            #break
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


workspace = "C:/Users/Simon/Documents/GitHub/mapmatcherTest"
fcname = "testRunnerTracks.shp"

