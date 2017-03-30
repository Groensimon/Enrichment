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
from shapely.geometry import MultiPoint, shape, LineString, mapping
import fiona


def buildNodeList(network):
    nodelist = {}
    with fiona.open(network, 'r') as source:
        number = 0
        for f in source:
            geom = shape(f['geometry'])
            #if number ==100:
               # break
            van = f['properties']['van_id']
            naar =f['properties']['naar_id']

            fp = geom.coords[0]
            lp = geom.coords[len(geom.coords)-1]
            update(van,fp,nodelist)
            update(naar,lp,nodelist)
            number+=1
    #print nodelist
    source.close()
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
        mp = MultiPoint([p for p in v])
        #print mp
        nodelistnew[k]=mp.centroid.coords[0]
    #print "966076: "+str(nodelistnew['966076'])
    return nodelistnew

def correctNetwork(nodelist, network):
    outname = os.path.join(os.path.dirname(network),((os.path.splitext(os.path.basename(network))[0][:9])+'_corr'))
    with fiona.open(network, 'r') as source:
        source_driver = source.driver
        source_crs = source.crs
        source_schema = source.schema

        with fiona.open(
               outname,
               'w',
               driver=source_driver,
               crs=source_crs,
               schema=source_schema) as c:

            for rec in source:
                geom = shape(rec['geometry'])
                p1 =  rec['properties']["van_id"]
                p2 =  rec['properties']["naar_id"]
                if p1 in nodelist:
                    first_point = nodelist[p1]
                else:
                    first_point = None
                if p2 in nodelist:
                   last_point = nodelist[p2]
                else:
                    last_point = None
                line = getNewLine(geom,first_point, last_point)
                rec['geometry'] = mapping(line)
                #print rec
##                if line.is_valid == False:
##                    print "invalid: "+str(list(line.coords))
##                    print "original: "+str(list(geom.coords))
##                    break
                c.write(rec)


    source.close()
    c.close()



def getNewLine(geom, first_point,last_point):
    array = list(geom.coords)
    #print array
    fp =[first_point]
    cf=1
    lp =[last_point]
    cl = len(array)-1
    if first_point ==None:
        fp =[]
        cf = 0
    if last_point == None:
        lp=[]
        cl = len(array)

    # Build a new array with your new point in the 0th position, and
    # the rest of the points from the old array.
    alist = fp+[array[x] for x in range(cf,cl)]
    blist = alist+lp
    new_array = blist
    # Then make a new Polyline object with that array.
    #print new_array
    geom.coords = blist
    return geom

def main():
    workspace="C:/Temp/fietsersbond"
    #network = "links.shp"

    network = os.path.join(workspace,"links.shp")
    nodelist = buildNodeList(network)
    #print nodelist
    nodelist = generateCentroids(nodelist)
    #print nodelist
    correctNetwork(nodelist,network)



if __name__ == '__main__':
    main()
