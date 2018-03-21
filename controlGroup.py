import sys
import json
import datetime
import os
from lib.db import DB

from impact.impact_analyzer import *
from import_detection.detector import *
from import_detection.general import *
from googleDrive.googleAPI import *
from lib.db import DB

# SET TO CORRECT COORDINATES
x = [513694000,-4465000]
y = [516374000,1921000]


# =======DO NOT CHANGE ============
# ====id of the folder files are shared on Drive
shared_drive_id = '1jS9wv4965g5eKFdKJ7RrW-yHHXkv9OqH'

# CREATE A GOOGLE API CONNECTOR OBJECT
googleDriveConnection =  googleAPI()


# Name of City Must be passed as an argument
if len(sys.argv) < 3:
        print("Usage: python controlGroup.py <DB name> <Path of JSON comparing to> <Detection Level (optionnal)>")
        sys.exit(-1)

city = sys.argv[1]
jsonPath = sys.argv[2]


# Optionnaly you can pass the detcetion level
detectionLevel = 20
if len(sys.argv) > 3:
    detectionLevel = int(sys.argv[3])

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

# =============================================================SETUP FOLDERS===============================================

import_dir = {}

# # MAKE THE LOCAL FOLDER
local_folder_root = os.getcwd() + '/' + city + 'CONTROLGROUP'
import_dir['local'] = os.getcwd() + '/' + city + 'CONTROLGROUP'
if not os.path.exists(import_dir['local']):
    os.makedirs(import_dir['local'])

google_folder_root_id = googleDriveConnection.createFolder(city+'CONTROLGROUP', shared_drive_id)
import_dir['google'] = google_folder_root_id


# =============================================================MAIN SCRIPT=================================================

jsondata = {}
with open(jsonPath, "r") as jsonFile:
    jsondata = json.load(jsonFile)


# ===============================================IMPACT ANALYSIS COMPARISON================================================

for iMport in jsondata:

	import_date = datetime.datetime.strptime(jsondata[iMport][0],'%Y-%m-%d')

	# ======= CREATE DIR FOR GRAPHS OF THIS SPECIFIC CITY======
	import_dir['local'] = import_dir['local'] + '/' +  import_date.strftime('%Y-%m-%d')
	if not os.path.exists(import_dir['local']):
		os.makedirs(import_dir['local'])

	# ================ CREATE DIR FOR GOOGLE DRIVE ==================
	import_dir['google'] = googleDriveConnection.createFolder(import_date.strftime('%Y-%m-%d'), import_dir['google'])

	# # GET THE USER GROUPS
	groups = group_analyserv2(db, import_date-relativedelta(months=+6), import_date)

	# # # FOR EACH ANALYSIS WE WANT TO LOOK AT impact afer 1 week, 1 month, 3 month
	time_intervals = [import_date+relativedelta(weeks=+1), import_date+relativedelta(months=+1), import_date+relativedelta(months=+3)]

	# ABNORMAL RETURN OF CONTRIBUTIONS PER GROUP (based on expected return of 6 month before the import)
	# 1 week, 1 month, 3 month
	for date_after in time_intervals:
		abnormal_return_for_group(db, googleDriveConnection, groups, import_date-relativedelta(months=+6) , import_date , date_after, dir_write_to =import_dir)

	# # EVOLUTION OF EDITS PERIOD
	# # 6 month after
	contribution_types_gobal_analysis(db, googleDriveConnection, import_date-relativedelta(months=+6),import_date,import_date+relativedelta(months=+6), None, None, import_dir)


	# # ABNORMAL RETURN OF MAINTENANCE RATIO PER GROUP
	# # 1 week, 1 month, 3 month
	for date_after in time_intervals:
		impact_import_creationtomaintenance_ratio_abnormal_return(db, googleDriveConnection, groups,  import_date-relativedelta(months=+6), import_date, date_after, import_dir)


	# # # # AMENITY EVOLUTION PER GROUP
	# # # # 1 week, 1 month, 3 month
	for date_after in time_intervals:
	 	top_amenity_evolution_per_group(db,googleDriveConnection, import_date-relativedelta(months=+6),import_date,date_after, None, None, import_dir)

	# # # SURVIVAL ANALYSIS
	# # # 1 week, 1 month, 3 months
	survivalAnalysis(db,googleDriveConnection, import_date-relativedelta(months=+6),import_date,import_dir)

	#END: ==============RESET THE FOLDERS=======
	import_dir['local'] = local_folder_root
	import_dir['google'] = google_folder_root_id









