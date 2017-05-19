#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Simon
#
# Created:     19-05-2017
# Copyright:   (c) Simon 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import json


with open("C:/thesisData/runnerTracks/EHV0.json") as json_data:
        data = json.load(json_data)
print len(data)

with open("C:/thesisData/runnerTracks/EHV1.json") as json_data:
        data = json.load(json_data)
print len(data)

with open("C:/thesisData/runnerTracks/EHV2.json") as json_data:
        data = json.load(json_data)
print len(data)

with open("C:/thesisData/runnerTracks/EHV3.json") as json_data:
        data = json.load(json_data)
print len(data)

with open("C:/thesisData/runnerTracks/EHV4.json") as json_data:
        data = json.load(json_data)
print len(data)

with open("C:/thesisData/runnerTracks/EHV5.json") as json_data:
        data = json.load(json_data)
print len(data)

with open("C:/thesisData/runnerTracks/EHV6.json") as json_data:
        data = json.load(json_data)
print len(data)

with open("C:/thesisData/runnerTracks/EHV7.json") as json_data:
        data = json.load(json_data)
print len(data)

with open("C:/thesisData/runnerTracks/EHV8.json") as json_data:
        data = json.load(json_data)
print len(data)

with open("C:/thesisData/runnerTracks/EHV9.json") as json_data:
        data = json.load(json_data)
print len(data)

with open("C:/thesisData/runnerTracks/EHV-clean.geojson") as json_data:
        data = json.load(json_data)
print len(data['features'])
