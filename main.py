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
with open('config.json') as json_file:
    config = json.load(json_file)

# ======== Create Database =======
db = DB(config['DB'])

<<<<<<< HEAD
# Detect import
# x = [501355000,298938000]
# y = [506677000,311696000]
x = [513694000,-4465000]  #en bas a gauche
y = [516374000,1921000] #en haut a droite
print(detectImport(db,'London',x,y))
# detectWaysImport(db,'London',x,y)
=======
# # Detect import
x = [513694000,-4465000]
y = [516374000,1921000]
>>>>>>> d17ff832b7daa31cdb434fb7e6c40e1b11db801b

# =============TEST==================

# Name of City

# text = input("Please enter the name of the city you would like to analyse: ")

city = "postgres" #str(text)
#dbname = "osm"+city.lower()

# with open("config.json", "r") as jsonFile:
#     data = json.load(jsonFile)

# tmp = data["DB"]["DB_NAME"]
# data["DB"]["DB_NAME"] = dbname

# with open("config.json", "w") as jsonFile:
#     json.dump(data, jsonFile)


#WALTHROUGH OF MAIN SCRIPT

# CREATE A GOOGLE API CONNECTOR OBJECT
googleDriveConnection =  googleAPI()

# CREATE DIR TO WRITE FILES TO
folder_info_of_city = {}

# MAKE THE GOOGLE DRIVE FOLDER
google_folder_root_id = googleDriveConnection.createFolder(city)
folder_info_of_city['google'] = google_folder_root_id

# MAKE THE LOCAL FOLDER
local_folder_root =  os.getcwd() + '/' + city
folder_info_of_city['local'] = os.getcwd() + '/' + city
if not os.path.exists(folder_info_of_city['local']):
    os.makedirs(folder_info_of_city['local'])

# # LIST OF THE IMPORT DETECTED FOR THE CITY
imports_normal = detectImport(db, city, x, y)
# #example [[datetime.datetime(2009, 8, 17, 0, 0), 'NaPTAN']]

# # EXTRA INFORMATION FOR EACH IMPORT
imports_normal_extra = imports_report(db, imports_normal)
#example 
# imports_normal_extra =[[[datetime.datetime(2009, 8, 17, 0, 0), 'NaPTAN'], [{u'bus_stop': 20100}], [{u'aircraft_fuel': 0}]]]

print("\n-------------Starting Impact Analysis-------------\n")

# Analyse Import by Import
for iMport in imports_normal_extra:
	analyse_import(db, googleDriveConnection, iMport, x, y, city, folder_info_of_city)
	folder_info_of_city['google'] = google_folder_root_id
	folder_info_of_city['local'] = local_folder_root





