import sys
import json
from import_detection.detector import *
from impact.impact_analyzer import *
from import_detection.colorgraph import *
import datetime

from lib.db import DB
from import_detection.detector import detectImport

# ======== Open Config =======
with open('config.json') as json_file:
    config = json.load(json_file)

# ======== Create Database =======
db = DB(config['DB'])

# # Detect import
x = [513694000,-4465000]
y = [516374000,1921000]

# =============TEST==================

# Name of City
city = 'London'

#WALTHROUGH OF MAIN SCRIPT

# LIST OF THE IMPORT DETECTED FOR THE CITY
imports_normal = detectImport(db, city, x, y)
#example [[datetime.datetime(2009, 8, 17, 0, 0), 'NaPTAN']]

# EXTRA INFORMATION FOR EACH IMPORT
imports_normal_extra = imports_report(db, imports_normal)
#example [[[datetime.datetime(2009, 8, 17, 0, 0), 'NaPTAN'], [{u'bus_stop': 20100}], [{u'aircraft_fuel': 0}]]]

print("-------------Starting Impact Analysis-------------")

# Analyse Import by Import
for iMport in imports_normal_extra:
	analyse_import(db, iMport, city, x, y)





