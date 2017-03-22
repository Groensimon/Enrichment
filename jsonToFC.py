#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Simon
#
# Created:     13-03-2017
# Copyright:   (c) Simon 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def main():
    pass

if __name__ == '__main__':
    main()


import arcpy
import json

arcpy.env.workspace = 'E:/module7/data/runnerTracks'




def GeoJSONToFC(workspace,inputData,fcname):

    with open(inputData) as json_data:
        data = json.load(json_data)

    #geodb = gdb
    #url = USGSurl
    #weburl = urllib2.urlopen(url)
    #if weburl.getcode() == 200:
        #data = json.loads(weburl.read())
    summary, trail = []
    #features = {}
    global data
    for i in data[0]["summary"]:
        ID, dist, time, place = i[0]["properties"][0]["_id"],i[0]["properties"][0]["distance"],i[0]["properties"][0]["duration"],i[0]["properties"][0]["country"]
        x,y = float(i["geometry"]["coordinates"][0]),float(i["geometry"]["coordinates"][1])
        tracks.append([ID,dist,time,place,[x,y]])
    runnerTracks0 = arcpy.CreateFeatureclass_management(workspace,fcname,"POINT",'','','',4326)
    arcpy.AddField_management(runnerTracks0,"ID","TEXT")
    arcpy.AddField_management(runnerTracks0, "Distance", "FLOAT")
    arcpy.AddField_management(runnerTracks0,"Duration", "FLOAT")
    arcpy.AddField_management(runnerTracks0, "Country", "TEXT")
    with arcpy.da.InsertCursor(runnerTracks0,["ID","Distance","Duration","Country","SHAPE@XY"]) as cur:
        for v in coordinates:
            ID = v[0]
            place = v[1]
            dist = v[2]
            time = v[3]
            pointGeometry = arcpy.PointGeometry(arcpy.Point(*v[4]))
            row = (ID,place,dist,time,pointGeometry)
            cur.insertRow(row)
            print row

workspace = "D:/runnerTracks"
inputData = "D:/runnerTracks/EHV0.json"
fcname = "tracks0"
GeoJSONToFC(workspace,inputData,fcname)