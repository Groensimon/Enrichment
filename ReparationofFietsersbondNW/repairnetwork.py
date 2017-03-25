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
            #if number ==100:
                #break
            van = row[0]
            naar = row[1]
            geom = row[2]
            fp = geom.firstPoint
            lp = geom.lastPoint
            update(van,fp,nodelist)
            update(naar,lp,nodelist)
            number+=1
    #print nodelist
##    print "966076: "+str(nodelist['966076'])
    return nodelist

def update(nid, point, nodelist):
##    if nid =='966076':
##        print point
    if nid in nodelist:
        nodelist[nid].append(point)
    else:
        nodelist[nid] = [point]

def generateCentroids(nodelist):
    nodelistnew = {}
    for k,v in nodelist.items():
        mp = MultiPoint([(p.X, p.Y) for p in v])
        #print mp
        nodelistnew[k]=arcpy.Point(mp.centroid.x, mp.centroid.y)
    #print "966076: "+str(nodelistnew['966076'])
    return nodelistnew





def correctNetwork(nodelist, network):
    outname = (os.path.splitext(os.path.basename(network))[0][:9])+'_corr'
    try:
        if arcpy.Exists(outname):
            arcpy.Delete_management(outname)
        arcpy.CopyFeatures_management(network, os.path.join(arcpy.env.workspace,outname)+'.shp')
    except Exception:
        e = sys.exc_info()[1]
        print(e.args[0])
    arcpy.Delete_management('segments_lyr')
    arcpy.MakeFeatureLayer_management(os.path.join(arcpy.env.workspace,outname)+'.shp', 'segments_lyr')
    cursor = arcpy.UpdateCursor('segments_lyr', ["van_id","naar_id","SHAPE@"])

    for r in cursor:
        geom = r.getValue("SHAPE")
        p1 =  r.getValue("van_id")
        p2 =  r.getValue("naar_id")
        if p1 in nodelist:
            first_point = nodelist[p1]
        else:
            first_point = None
        if p2 in nodelist:
           last_point = nodelist[p2]
        else:
            last_point = None

        r.setValue("SHAPE",getNewLine(geom,first_point, last_point))
        cursor.updateRow(r)

    del r,cursor



def getNewLine(geom, first_point,last_point):
    array = geom.getPart(0)
    fp =[first_point]
    cf=1
    lp =[last_point]
    cl = array.count-1
    if first_point ==None:
        fp =[]
        cf = 0
    if last_point == None:
        lp=[]
        cl = array.count

    # Build a new array with your new point in the 0th position, and
    # the rest of the points from the old array.
    alist = fp+[array.getObject(x) for x in range(cf,cl)]
    blist = alist+lp
    new_array = arcpy.Array(blist)
    # Then make a new Polyline object with that array.
    new_line = arcpy.Polyline(new_array)
    return new_line

def main():
    arcpy.env.workspace="C:\Temp\Road_293162"
    network = "Road_293162.shp"
    #network = "RoadTest.shp"
    nodelist = buildNodeList(network)
    nodelist = generateCentroids(nodelist)
    correctNetwork(nodelist,network)



if __name__ == '__main__':
    main()
