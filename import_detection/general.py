import sys
import datetime
from dateutil.relativedelta import relativedelta
import os
from impact.impact_analyzer import *
from import_detection.colorgraph import *
from googleDrive.googleAPI import *
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------
#Class containing the functions that generalise the results of impact analysis
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------

def analyse_import(db, googleDriveConnection, iMport, x = None, y = None, city = '', import_dir =''):

	#===IMPORT===DATE===
	import_date = iMport[0][0]

	# ======= CREATE DIR FOR GRAPHS OF THIS SPECIFIC IMPORT======
	import_dir['local'] = import_dir['local'] + '/' +  import_date.strftime('%Y-%m-%d')
	if not os.path.exists(import_dir['local']):
		os.makedirs(import_dir['local'])

	# ================ CREATE DIR FOR GOOGLE DRIVE ==================
	import_dir['google'] = googleDriveConnection.createFolder(import_date.strftime('%Y-%m-%d'), import_dir['google'])


	# PRINT THE NODES OF THIS IMPORT
	#draw_heatMap(db, googleDriveConnection, iMport, x, y, city, import_dir)

	# GET THE USER GROUPS
	groups = group_analyserv2(db, import_date-relativedelta(months=+6), import_date, x, y)

	print(groups)
	#sys.exit(-1)
	# # FOR EACH ANALYSIS WE WANT TO LOOK AT impact afer 1 week, 1 month, 3 month
	time_intervals = [import_date+relativedelta(weeks=+1), import_date+relativedelta(months=+1), import_date+relativedelta(months=+3)]

	# # ABNORMAL RETURN OF CONTRIBUTIONS PER GROUP (based on expected return of 6 month before the import)
	# # 1 week, 1 month, 3 month
	for date_after in time_intervals:
		abnormal_return_for_group(db, googleDriveConnection, groups, import_date-relativedelta(months=+6) , import_date , date_after, x, y, import_dir)

	# EVOLUTION OF EDITS PERIOD
	# 6 month after
	contribution_types_gobal_analysis(db, googleDriveConnection, import_date-relativedelta(months=+6),import_date,import_date+relativedelta(months=+6), x, y, import_dir)


	# ABNORMAL RETURN OF CONTRIBUTIONS PER GROUP
	# 1 week, 1 month, 3 month
	for date_after in time_intervals:
		impact_import_creationtomaintenance_ratio_abnormal_return(db, googleDriveConnection, groups,  import_date-relativedelta(months=+6), import_date, date_after, import_dir)

	# # # AMENITY EVOLUTION PER GROUP
	# # # 1 week, 1 month, 3 month
	# for x in range(0,3):
	# top_amenity_evolution_per_group(db,groups, iMport, date_before,event_date,date_after, x=None, y=None)

	# # AMENITY EVOLUTION PER GROUP
	# # 1 week, 1 month, 3 month
	for date_after in time_intervals:
		top_amenity_evolution_per_group(db,googleDriveConnection, import_date-relativedelta(months=+6),import_date,date_after, iMport, x, y, import_dir)
		top_import_amenity_abnormal_return(db,googleDriveConnection, import_date-relativedelta(months=+6),import_date,date_after, iMport, x, y, import_dir)

	# # SURVIVAL ANALISIS
	# # run the survival analysis for the



	#Keeping track of each graph ids and their corresponding imports (look into tacking screenshots for each graph we produce)
	#Compare to well chosen Control Groups !!!!!!!!!!!!
	#this function should return information helping us decipher quickly what graphs correspond to which imports
