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
	draw_heatMap(db, googleDriveConnection, iMport, x, y, city, import_dir)

	# GET THE USER GROUPS
	# groups = group_analyser(db, import_date-relativedelta(months=+6), import_date, x, y)

	# # FOR EACH ANALYSIS WE WANT TO LOOK AT impact afer 1 week, 1 month, 3 month
	# time_intervals = [import_date+relativedelta(weeks=+1), import_date+relativedelta(months=+1), import_date+relativedelta(months=+3)]
	
	# # # ABNORMAL RETURN OF CONTRIBUTIONS PER GROUP (based on expected return of 6 month before the import)
	# # # 1 week, 1 month, 3 month
	# for date_after in time_intervals:
	# 	abnormal_return_for_group(db, groups, import_date+relativedelta(months=+6) , import_date , date_after, x, y, import_dir)
	# 	break

	# # # EVOLUTION OF EDITS PERIOD 
	# # # 1 week, 1 month, 3 month
	# for x in range(0,3):
	# 	contribution_types_gobal_analysis(db, date_before,event_date,date_after, x=None, y=None)


	# # # ABNORMAL RETURN OF CONTRIBUTIONS PER GROUP
	# # # 1 week, 1 month, 3 month
	# for x in range(0,3):
	# 	impact_import_creationtomaintenance_ratio_abnormal_return(db, groups, date_before, event_date, date_after)

	# # # AMENITY EVOLUTION PER GROUP
	# # # 1 week, 1 month, 3 month
	# for x in range(0,3):
	top_amenity_evolution_per_group(db,googleDriveConnection, groups, date_before,event_date,date_after, iMport x=None, y=None)

	# # SURVIVAL ANALISIS
	# # run the survival analysis for the 	



	#Keeping track of each graph ids and their corresponding imports (look into tacking screenshots for each graph we produce)
	#Compare to well chosen Control Groups !!!!!!!!!!!!
	#this function should return information helping us decipher quickly what graphs correspond to which imports
	
