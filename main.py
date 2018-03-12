import sys
import json
from import_detection.detector import *
from impact.impact_analyzer import *
import datetime

from lib.db import DB
from import_detection.detector import detectImport

# ======== Open Config =======
with open('config.json') as json_file:
    config = json.load(json_file)

# ======== Create Database =======
db = DB(config['DB'])

# Detect import
x = [513694000,-4465000]
y = [516374000,1921000]

#WALTHROUGH OF MAIN SCRIPT
imports_normal = detectImport(db, 'London', x, y)
# imports_ways = detectWaysImport(db, 'London', x, y) #example [[datetime.datetime(2009, 8, 17, 0, 0), 'NaPTAN']]

imports_normal = imports_report(db, imports_normal)
# imports_ways = imports_report(db, imports_ways) #example [[[datetime.datetime(2009, 8, 17, 0, 0), 'NaPTAN'], [{u'bus_stop': 20100}], [{u'aircraft_fuel': 0}]]]

#run the analysis
print("-------------Starting Impact Analysis-------------")
#script which launches the graphs and produces an output giving us information on what graph corresponds to what import
#Go one import at a time
#For each import we want to run all the analysis we have
#Keeping track of each graph ids and their corresponding imports (look into tacking screenshots for each graph we produce)
#Compare to well chosen Control Groups !!!!!!!!!!!!
#this function should return information helping us decipher quickly what graphs correspond to which imports





