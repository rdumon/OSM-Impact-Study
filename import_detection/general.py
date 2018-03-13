import sys
from impact_analyzer.py import *
import datetime

#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------
#Class containing the functions that generalise the results of impact analysis
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------

def analyse_import(db, iMport, city='', x = None, y = None):

	#===IMPORT===DATE===
	import_date = iMport[0]

	# PRINT THE NODES OF THIS IMPORT
	draw_heatMap(db, iMport, city)

	# FIND THE GROUPS
	groups = group_analyser(db, date_before, event_date)

	# ABNORMAL RETURN OF CONTRIBUTIONS PER GROUP
	# 1 week, 1 month, 3 month
	abnormal_return_for_group(db, groups, date_before, event_date , date_after, x = None, y = None)

	# EVOLUTION OF EDITS PERIOD 
	# 1 week, 1 month, 3 month


	# ABNORMAL RETURN OF CONTRIBUTIONS PER GROUP
	# 1 week, 1 month, 3 month


	#Keeping track of each graph ids and their corresponding imports (look into tacking screenshots for each graph we produce)
	#Compare to well chosen Control Groups !!!!!!!!!!!!
	#this function should return information helping us decipher quickly what graphs correspond to which imports
	
