#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      simon
#
# Created:     22/03/2017
# Copyright:   (c) simon 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os
import arcpy
arcpy.env.overwriteOutput = True
from shapely.geometry import MultiPoint


def buildNodeList(network):
    nodelist = {}
    if arcpy.Exists(network):
        cursor = arcpy.da.SearchCursor(network, ["van_id", "naar_id", "SHAPE@"])
        number = 0
        for row in cursor:
            if number ==100:
                break
            van = row[0]
            naar = row[1]
            geom = row[2]
            fp = geom.firstPoint
            lp = geom.lastPoint
            update(van,fp,nodelist)
            update(naar,lp,nodelist)
            number+=1
    #print nodelist
    return nodelist

def generateCentroids(nodelist):
    nodelistnew = {}
    for k,v in nodelist.items():
        mp = MultiPoint([(p.X, p.Y) for p in v])
        #print mp
        nodelistnew[k]=arcpy.PointGeometry(arcpy.Point(mp.centroid.x, mp.centroid.y))
    return nodelistnew



def update(nid, point, nodelist):
    if nid in nodelist:
        nodelist[nid].append(point)
    else:
        nodelist[nid] = [point]


def main():
    arcpy.env.workspace="C:\Users\simon\Documents\GitHub\Enrichment"
    network = "networkProjected.shp"
    nodelist = buildNodeList(network)
    nodelist = generateCentroids(nodelist)


if __name__ == '__main__':
    main()
