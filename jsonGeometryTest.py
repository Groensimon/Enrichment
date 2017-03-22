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

def main():
    pass

if __name__ == '__main__':
    main()

import json
import pygeoj

"""
with open('D:/runnerTracks/EHV0.json') as d:
    data = json.load(d)

for feature in data['features']:
    print feature['geometry']['type']
    print feature['geometry']['coordinates']
"""

data = pygeoj.load("D:/runnerTracks/EHV0.json")
for feature in data:
    print feature.geometry.type
    print feature.geometry.coordinates