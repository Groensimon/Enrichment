#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Simon Groen
#
# Created:     11-04-2017
# Copyright:   (c) Simon 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import numpy
import os
from shapely.geometry import MultiPoint, shape, LineString, mapping
#import fiona
import arcpy
import math

"""
def MMin(networkFoot):
    partnum = 0
    feat = networkFoot
 # Count the number of points in the current multipart feature
    #partcount = feat.partCount
    pntcount = 0
    mmin = 1000000000
 # Enter while loop for each part in the feature (if a singlepart feature
 # this will occur only once)
    while partnum < partcount:
        part = feat.getPart(partnum)
        pnt = part.next()
  # Enter while loop for each vertex
    while pnt:
        pntcount += 1
        if mmin > pnt.M:
            mmin = pnt.M
        pnt = part.next()
   # If pnt is null, either the part is finished or there is an
   # interior ring
        if not pnt:
            pnt = part.next()
    partnum += 1
    return mmin


def MMax(networkFoot):
    partnum = 0
    feat = networkFoot
 # Count the number of points in the current multipart feature
    partcount = feat.partCount
    pntcount = 0
    mmax = -1000000000
 # Enter while loop for each part in the feature (if a singlepart feature
 # this will occur only once)
    while partnum < partcount:
        part = feat.getPart(partnum)
        pnt = part.next()
  # Enter while loop for each vertex
    while pnt:
        pntcount += 1
        if mmax < pnt.M:
            mmax = pnt.M
        pnt = part.next()
   # If pnt is null, either the part is finished or there is an
   # interior ring
        if not pnt:
            pnt = part.next()
    partnum += 1
    return mmax
"""

#Try this with the complete OSM road network and then after, exclude all the normal roads!!!

def addMToNetwork(networkFoot, outFeatures):
    if arcpy.Exists(outFeatures):
        arcpy.Delete_management(outFeatures)
    # Fieldname containing the measured length for each line
    # if null, then the map length will be used
    mlField="meas_len"

    # Output feature class settings
    inFeatures = networkFoot
    out_path = "C:/thesisData"
    out_name = "Pedestrian_roads_wM.shp"
    geometry_type = "POLYLINE"
    template = inFeatures
    spatial_reference = inFeatures
    has_m = "ENABLED"
    has_z = "DISABLED"

    # Create the new shapefile
    arcpy.CreateFeatureclass_management(out_path, out_name, geometry_type, template, has_m, has_z, spatial_reference)

    #
    # Create a list of fields to use when copying field values from input to output
    #
    fields = arcpy.ListFields(inFeatures)
    fieldList = []
    for field in fields:
      fieldList.append(field.name)



    # Loop through input features
    rows=arcpy.SearchCursor(networkFoot)

    # Output features
    outFeatures=out_path+"/"+out_name

    # Open insertcursor
    #
    outRows = arcpy.InsertCursor(outFeatures)

    # Create point and array objects
    #
    pntObj = arcpy.Point()
    arrayObj = arcpy.Array()

    shapeName=arcpy.Describe(networkFoot).shapeFieldName #Get shape field name
    featType=arcpy.Describe(networkFoot).shapeType       # Get feature type
    isMeasured=arcpy.Describe(networkFoot).hasM  # Check if its a polylineM feature already

    # Record counter
    i=1

    # Loop through input shapefile
    for row in rows:
        print "Processing row %d " % i
        feat=row.getValue(shapeName)
        noparts=feat.partCount
        partno = 0
        currentM=0
        # Loop through geometry parts
        for part in feat:
            pntCounter=0;
            segmentDistance=0
            prevX=0
            prevY=0
            # Loop through points in part
            for pnt in feat.getPart(partno):
              if pntCounter == 0: # First point
                prevX=pnt.X
                prevY=pnt.Y
                pntObj.X=pnt.X
                pntObj.Y=pnt.Y
                pntObj.M=0
              else:
                curX=pnt.X
                curY=pnt.Y
                # Calculate segment length
                segmentDistance = math.sqrt(math.pow((curX-prevX),2) + math.pow((curY-prevY),2))
                # Use the measured distance
                if mlField <> "":
                    segmentDistance=segmentDistance/feat.length*row.getValue(mlField)
                # Add previous M to segment length
                currentM=currentM + segmentDistance
                pntObj.X=pnt.X
                pntObj.Y=pnt.Y
                pntObj.M=currentM
                prevX=pnt.X
                prevY=pnt.Y
              # Add measured points to array
              arrayObj.add(pntObj)
              pntCounter=pntCounter+1
        # Create new row
        #
        outFeat=outRows.newRow()

        # Copy attributes to new row
        #
        for fieldName in fieldList:
          if fieldName not in  ("FID", "Shape"): # ignore FID and Shape fields
            outFeat.setValue(fieldName, row.getValue(fieldName))

        # Assign array of PointMs to new feature
        outFeat.shape=arrayObj

        # Insert feature
        outRows.insertRow(outFeat)

        # Clear array of points
        #
        arrayObj.removeAll()
        i=i+1

    # Remove cursor from memory
    del outRows
    del rows



#def networkLinking():
    #with fiona.open(networkBike, 'r') as bike: #and with fiona.open(networkFoot, 'r') as foot:


def appendedNetwork(networkBike, networkFoot, outData):
    if arcpy.Exists(outData):
        arcpy.Delete_management(outData)
    arcpy.FeatureToLine_management([networkBike,networkFoot], outData, "", "ATTRIBUTES")


#def buildNodeList():



#def updateNodeList():




def main():
    workspace = "C:/thesisData"
    networkBike = "C:/thesisData/network/links_corr/links_corr.shp"
    networkFoot = "C:/thesisData/Pedestrian_roads_rdnew.shp"
    outFeatures = "C:/thesisData/Pedestrian_roads_wM.shp"
    outdata = "C:/thesisData/combinedNetwork.shp"
    #network = os.path.join(workspace,"links.shp")
    #appendedNetwork(networkBike,networkFoot,outdata)
    addMToNetwork(networkFoot, outFeatures)

main()

