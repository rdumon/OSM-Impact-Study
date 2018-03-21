import sys
import json
import datetime
import os

from impact.impact_analyzer import *
from import_detection.detector import *
from import_detection.general import *
from googleDrive.googleAPI import *
from lib.db import DB


# =======DO NOT CHANGE ============
# ====id of the folder files are shared on Drive
shared_drive_id = '1jS9wv4965g5eKFdKJ7RrW-yHHXkv9OqH'

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
    print("Usage: python main.py <DB name> <Detection Level (optionnal)> <x[0]> <x[1]> <y[0]> <y[1]>")
    sys.exit(-1)

city = sys.argv[1]

# Optionnaly you can pass the detcetion level
detectionLevel = 20
if len(sys.argv) > 2:
    detectionLevel = int(sys.argv[2])

if len(sys.argv) > 6:
    x[0] = int(sys.argv[3])
    x[1] = int(sys.argv[4])
    y[0] = int(sys.argv[5])
    y[1] = int(sys.argv[6])
    print("Coordinates set.")

#  Configure db
with open("config.json", "r") as jsonFile:
    data = json.load(jsonFile)

tmp = data["DB"]["DB_NAME"]
data["DB"]["DB_NAME"] = city

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
google_folder_root_id = googleDriveConnection.createFolder(city, shared_drive_id)
folder_info_of_city['google'] = google_folder_root_id

# # MAKE THE LOCAL FOLDER
local_folder_root = os.getcwd() + '/' + city
folder_info_of_city['local'] = os.getcwd() + '/' + city
if not os.path.exists(folder_info_of_city['local']):
    os.makedirs(folder_info_of_city['local'])

# LIST OF THE IMPORT DETECTED FOR THE CITY
imports_normal = detectImport(db, city, x, y, folder_info_of_city, googleDriveConnection ,detectionLevel)

# EXTRA INFORMATION FOR EACH IMPORT
imports_normal_extra = imports_report(db, googleDriveConnection, imports_normal, folder_info_of_city)

print("\n-------------Starting Impact Analysis (look Romain I fixed the typo)-------------\n")

# Analyse Import by Import
for iMport in imports_normal_extra:
	analyse_import(db, googleDriveConnection, iMport, x, y, city, folder_info_of_city)
	folder_info_of_city['google'] = google_folder_root_id
	folder_info_of_city['local'] = local_folder_root
