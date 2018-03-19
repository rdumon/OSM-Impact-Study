import sys
import json
import datetime
import os

from impact.impact_analyzer import *
from import_detection.detector import *
from import_detection.general import *
from googleDrive.googleAPI import *
from lib.db import DB

# ======== Open Config =======
# with open('config.json') as json_file:
#     config = json.load(json_file)

# ======== Create Database =======
# db = DB(config['DB'])

# # Detect import
x = [437240180,74091370]
y = [437516580,74390270]



# =============TEST==================

# Name of City Must be passed as an argument
if len(sys.argv) < 2:
        print("Usage: python main.py <Name of the City> <Detection Level (optionnal)>")
        sys.exit(-1)

city = sys.argv[1]

# Optionnaly you can pass the detcetion level
detectionLevel = 20
if len(sys.argv) > 2:
    detectionLevel = int(sys.argv[2])

#  Configure db
dbname = "osm"+city.lower()
with open("config.json", "r") as jsonFile:
    data = json.load(jsonFile)

tmp = data["DB"]["DB_NAME"]
data["DB"]["DB_NAME"] = dbname

with open("config.json", "w") as jsonFile:
    json.dump(data, jsonFile)

with open('config.json') as json_file:
    config = json.load(json_file)
db = DB(config['DB'])

#WALTHROUGH OF MAIN SCRIPT

# CREATE A GOOGLE API CONNECTOR OBJECT
googleDriveConnection =  googleAPI()

# CREATE DIR TO WRITE FILES TO
folder_info_of_city = {}

# MAKE THE GOOGLE DRIVE FOLDER
google_folder_root_id = googleDriveConnection.createFolder(city)
folder_info_of_city['google'] = google_folder_root_id

# # MAKE THE LOCAL FOLDER
folder_info_of_city['local'] = os.getcwd() + '/' + city
if not os.path.exists(folder_info_of_city['local']):
    os.makedirs(folder_info_of_city['local'])

# LIST OF THE IMPORT DETECTED FOR THE CITY
imports_normal = detectImport(db, city, x, y, folder_info_of_city, googleDriveConnection ,detectionLevel)
#example [[datetime.datetime(2009, 8, 17, 0, 0), 'NaPTAN']]

# EXTRA INFORMATION FOR EACH IMPORT
# imports_normal_extra = imports_report(db, imports_normal)
#example
# imports_normal_extra =[[[datetime.datetime(2009, 8, 17, 0, 0), 'NaPTAN'], [{u'bus_stop': 20100}], [{u'aircraft_fuel': 0}]]]

print("\n-------------Starting Impact Analysis-------------\n")

# Analyse Import by Import
# for iMport in imports_normal_extra:
# 	analyse_import(db, googleDriveConnection, iMport, x, y, city, folder_info_of_city)
# 	folder_info_of_city['google'] = google_folder_root_id
