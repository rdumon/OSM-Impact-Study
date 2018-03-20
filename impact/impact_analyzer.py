import sys
import json
import decimal
import datetime
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import operator
import numpy as np
plotly.tools.set_credentials_file(username='RomainDumon', api_key='cJVtOQ4pZHAaQcBeTULV')
sys.path.insert(0, '../import_detection/')
from import_detection.detector import *

sys.path.insert(0, '../lib/')
from lib.amenities import *

from googleDrive.googleAPI import *
# from db import DB

#LIST OF FUNCTIONS IN THIS FILE:

# def abnormal_return_for_group(db, groups, date_before, event_date , date_after, x = None, y = None)
# counts abnormal  WAYS/NODES/RELATIONS

# def contribution_types_gobal_analysis(db, date_before,event_date,date_after, x=None, y=None)
# evolution of edits/creations/delete over a period of time of WAYS/NODES/RELATIONS

# def impact_import_creationtomaintenance_ratio(db, groups, date_before, event_date, Graph_title)
# WAYS/NODES/RELATIONS

# def impact_import_creationtomaintenance_ratio_abnormal_return(db, groups, date_before, event_date, date_after)
# WAYS/NODES/RELATIONS

# def top_amenity_evolution_per_group(db,groups, date_before,event_date,date_after, x=None, y=None)
# NODES

# def group_analyser(db, date_before, event_date)
# WAYS/NODES/RELATIONS

# def trim_95Perc_rule(data)



#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------
#ANALYSING FUNCTIONS
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------

#==================================================================================
#=========All dates should have the format 'YearMonthDate' i.e. '20090311'=========
#==================================================================================
def abnormal_return_for_group(db, googleDriveConnection, groups, date_before, event_date , date_after, x = None, y = None, dir_write_to =None):

	# If there is a location restriction
	where_clause = ' '
	if x!=None and y!=None and len(x) == 2 and len(y) == 2:
		where_clause += 'AND latitude > '+str(x[1])+' AND longitude > '+str(x[0])+' AND latitude < '+str(y[1])+' AND longitude < '+str(y[0])

	#The number of weeks between event date and the date before the event
	diff_expected_user = (event_date - date_before).days /7
	#The number of weeks between event date and the date after the event
	diff_actual_user = (date_after - event_date).days /7

	#Average number of edits per user per week for the six months before
  	#This query is location proof
	expected_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d')+"'"+ where_clause + " GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d') + "' GROUP BY user_name) UNION ALL (SELECT count(*) as contributions, user_name from relations where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d') + "' GROUP BY user_name)) SELECT (SUM(contributions)/"+str(diff_expected_user)+") as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions)"])

	expected = {}

	for a in expected_per_user:
		expected[a[1]] = a[0]

	#query average contribution for each user in each group
	actual_one_month = {}
	actual_per_user_one_month = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at > '" + event_date.strftime('%Y-%m-%d') + "' AND created_at < '" + date_after.strftime('%Y-%m-%d') +"'"+ where_clause + " GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at > '" + event_date.strftime('%Y-%m-%d') + "' AND created_at < '" + date_after.strftime('%Y-%m-%d') + "' GROUP BY user_name) UNION ALL (SELECT count(*) as contributions, user_name from relations where created_at > '" + event_date.strftime('%Y-%m-%d') + "' AND created_at < '" + date_after.strftime('%Y-%m-%d') + "' GROUP BY user_name)) SELECT (SUM(contributions)/"+str(diff_actual_user)+") as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions)"])
	for a in actual_per_user_one_month:
		actual_one_month[a[1]] = a[0]

	abnormalReturnPerUser_one_month = {}
	for group in groups:
		for user in group:
			abnormalReturnPerUser_one_month[user] = actual_one_month.get(user,decimal.Decimal(0.0)) - expected.get(user,decimal.Decimal(0.0))

	dataAbnormal = []
	for group in groups:
		data = []
		for user in group:
			data.append(abnormalReturnPerUser_one_month[user])
		dataAbnormal.append(data)

	group_1 = go.Box(
    	y=dataAbnormal[0],
    	name = 'Group 1',
    	boxpoints = False,
	)
	group_2 = go.Box(
    	y=dataAbnormal[1],
    	name = 'Group 2',
    	boxpoints = False,
	)
	group_3 = go.Box(
    	y=dataAbnormal[2],
    	name = 'Group 3',
    	boxpoints = False,
	)
	group_4 = go.Box(
    	y=dataAbnormal[3],
    	name = 'Group 4',
    	boxpoints = False,
	)
	group_5 = go.Box(
    	y=dataAbnormal[4],
    	name = 'Group 5',
    	boxpoints = False,
	)

	# find max and min for ranges in layout 
	maxVal = 0
	minVal = 0
	for data in dataAbnormal:
		if np.amax(data) > maxVal:
			maxVal = np.amax(data)
		if np.amin(data) < minVal:
			minVal = np.amin(data)

	layout = go.Layout(
		title = "Abnormal Return " +str(diff_actual_user) + " weeks after event",
	    width=1200, height=540,
	    yaxis = dict(range = [minVal,maxVal]),

	)

	data = [group_1,group_2,group_3,group_4,group_5]
	fig = dict(data = data, layout = layout)

	# py.plot(data,filename='box-plots osm London month')
	filelocation = dir_write_to['local']+'/abnormalReturnContrib'+str(diff_actual_user)+'weekAfter-'+date_after.strftime('%Y-%m-%d')+'.png'
	py.image.save_as(fig,filename = filelocation)

	# #=====UPLOAD TO GOOGLE DRIVE====
	filename = 'abnormalReturnContrib-'+str(diff_actual_user)+'weekAfter.png'
	googleDriveConnection.upload_GoogleDrive(filename,filelocation, dir_write_to['google'], 'photo/png')

	# ==== SET UP FOR JSON
	filename = "abnormalReturnContrib-"+str(diff_actual_user)+"weekAfter"+".json"
	filelocation = dir_write_to['local']+"/"+filename

	# == CHANGE DECIMAL OBJECTS TO FLOAT DATA POINTS
	for data in dataAbnormal:
		for i in range(0,len(data)):
			data[i] = float(data[i])
	json_info = { "data " : dataAbnormal}

	#====MAKE JSON======
	with open(filelocation, "w") as f:
		json.dump(json_info, f)

	# UPLOAD TO GOOGLE DRIVE
	googleDriveConnection.upload_GoogleDrive(filename,filelocation, dir_write_to['google'], 'text/json')

#=================================================================================================
#=========Looking at evolution of deletes/creation and edits per day for a certain period=========
#=================================================================================================
def contribution_types_gobal_analysis(db, googleDriveConnection, date_before,event_date,date_after, x=None, y=None, dir_write_to = None):

	#work out evolution of delete contributions
	delete_per_day = db.execute(["with C as((SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM nodes WHERE  created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after.strftime('%Y-%m-%d')+"'"+ " AND deleted = true GROUP BY created_at) UNION ALL (SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM ways WHERE  created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after.strftime('%Y-%m-%d')+"'"+ " AND deleted = true GROUP BY created_at) UNION ALL (SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM relations WHERE  created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after.strftime('%Y-%m-%d')+"'"+ " AND deleted = true GROUP BY created_at)) SELECT created_at,SUM(contrib_deletion) as sum_contrib_deletion FROM C GROUP BY created_at ORDER BY created_at" ])

	# TODO
	delete_per_day_x = []
	delete_per_day_y = []
	for a in delete_per_day:
		delete_per_day_x.append((datetime.datetime.strptime(a[0],'%Y%m%d')).strftime('%Y-%m-%d'))
		delete_per_day_y.append(a[1])


	#work out evolution of creation contributions
	creation_per_day = db.execute(["with C as((SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM nodes WHERE  created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after.strftime('%Y-%m-%d')+"'"+ " AND version = 1 GROUP BY created_at) UNION ALL (SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM ways WHERE  created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after.strftime('%Y-%m-%d')+"'"+ " AND version = 1 GROUP BY created_at) UNION ALL (SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM relations WHERE  created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after.strftime('%Y-%m-%d')+"'"+ " AND version = 1 GROUP BY created_at)) SELECT created_at,SUM(contrib_deletion) as sum_contrib_deletion FROM C GROUP BY created_at ORDER BY created_at" ])

	creation_per_day_x = []
	creation_per_day_y = []
	for a in creation_per_day:
		creation_per_day_x.append((datetime.datetime.strptime(a[0],'%Y%m%d')).strftime('%Y-%m-%d'))
		creation_per_day_y.append(a[1])

	# #work out evolution of edits contributions
	edits_per_day = db.execute(["with C as((SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM nodes WHERE  created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after.strftime('%Y-%m-%d')+"'"+ " AND deleted = false AND version != 1 GROUP BY created_at) UNION ALL (SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM ways WHERE  created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after.strftime('%Y-%m-%d')+"'"+ " AND deleted = false AND version != 1 GROUP BY created_at) UNION ALL (SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM relations WHERE  created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after.strftime('%Y-%m-%d')+"'"+ " AND deleted = false AND version != 1 GROUP BY created_at)) SELECT created_at,SUM(contrib_deletion) as sum_contrib_deletion FROM C GROUP BY created_at ORDER BY created_at" ])

	edits_per_day_x = []
	edits_per_day_y = []
	for a in edits_per_day:
		edits_per_day_x.append((datetime.datetime.strptime(a[0],'%Y%m%d')).strftime('%Y-%m-%d'))
		edits_per_day_y.append(a[1])

	#plotting
	trace1 = go.Scatter(
    x = delete_per_day_x,
    y = delete_per_day_y,
    mode = 'lines+markers',
    name = 'Number of Delete per Day'
	)

	trace2 = go.Scatter(
    x = creation_per_day_x,
    y = creation_per_day_y,
    mode = 'lines+markers',
    name = 'Number of Creation per Day'
	)

	trace3 = go.Scatter(
    x = edits_per_day_x,
    y = edits_per_day_y,
    mode = 'lines+markers',
    name = 'Number of Edits per Day'
	)

	trace4 = go.Scatter(
    x = [event_date.strftime('%Y-%m-%d'),event_date.strftime('%Y-%m-%d')],
    y = [-20,70000],
    mode = 'lines',
    name = 'Day of Import'
	)

	layout = go.Layout(
		title = "Evolution of Edits/Delete/Create 6 month before&after event",
	    width=1200, height=540,
	)

	data = [trace1,trace2,trace3,trace4]
	fig = dict(data = data, layout = layout)

	# py.plot(data,filename='box-plots osm London month')
	filelocation = dir_write_to['local']+'/evolutionMaintenance.png'
	py.image.save_as(fig,filename = filelocation)

	# UPLOAD TO GOOGLE DRIVE
	filename = 'evolutionMaintenance.png'
	googleDriveConnection.upload_GoogleDrive(filename,filelocation, dir_write_to['google'])


#=================================================================================================
#==================Impact of an import on creation to maintenance ratio===========================
#==================Date before is included and event_date is not included=========================
#=================================================================================================
def impact_import_creationtomaintenance_ratio(db, groups, date_before, event_date, Graph_title):

	#Dates computations
	event_date_convert = datetime.strptime(event_date,'%Y%m%d')
	date_before_convert = datetime.strptime(date_before,'%Y%m%d')

	#dictionaries recording the creates and total contribs of each user 
	dict_user_total_contribs = {}
	dict_user_creates = {}

	contribs_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d')+"' GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d') + "' GROUP BY user_name) UNION ALL (SELECT count(*) as contributions, user_name from relations where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d') + "' GROUP BY user_name)) SELECT SUM(contributions) as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions)"])

	for a in contribs_per_user:
		dict_user_total_contribs[a[1]] = a[0]


	creates_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d')+"' AND version = 1 GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d') + "' AND version = 1 GROUP BY user_name) UNION ALL (SELECT count(*) as contributions, user_name from relations where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d') + "'AND version = 1 GROUP BY user_name)) SELECT SUM(contributions) as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions)"])

	for a in creates_per_user:
		dict_user_creates[a[1]] = a[0]

	creations_group = [0,0,0,0,0]
	maintenance_group = [0,0,0,0,0]
	total_contribs_group = [0,0,0,0,0]

	for i in range(0,5):
		for user in groups[i]:
			creations_group[i] += dict_user_creates.get(user,decimal.Decimal(0.0))
			maintenance_group[i] += dict_user_total_contribs.get(user,decimal.Decimal(0.0)) - dict_user_creates.get(user,decimal.Decimal(0.0))
			total_contribs_group[i] += dict_user_total_contribs.get(user,decimal.Decimal(0.0))

	for i in range(0,5):
		creations_group[i] /=  total_contribs_group[i]
		maintenance_group[i] /=  total_contribs_group[i]

	trace1 = go.Bar(
    	x=['Group 1', 'Group 2', 'Group 3', 'Group 4', 'Group 5'],
    	y=creations_group,
    	name='Creates'
	)
	trace2 = go.Bar(
    	x=['Group 1', 'Group 2', 'Group 3', 'Group 4', 'Group 5'],
    	y=maintenance_group,
    	name='Maintenance'
	)

	data = [trace1, trace2]
	layout = go.Layout(
    	barmode='stack'
	)

	fig = go.Figure(data=data, layout=layout)
	py.plot(fig, filename='Maintenance vs Creations ' + Graph_title)


#=================================================================================================
#==================Impact of an import on creation to maintenance ratio===========================
#==================Using abdnormal return and box plost to show the rela.=========================
#=================================================================================================
def impact_import_creationtomaintenance_ratio_abnormal_return(db, googleDriveConnection, groups, date_before, event_date, date_after, dir_write_to):

	#The number of weeks between event date and the date before the event
	diff_expected_user = (event_date - date_before).days /7
	#The number of weeks between event date and the date after the event
	diff_actual_user = (date_after - event_date).days /7

	#dictionaries recording the creates and total contribs of each user 
	dict_user_total_contribs = {}
	dict_user_creates = {}

	contribs_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d')+" 00:00:00' GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d') + " 00:00:00' GROUP BY user_name) UNION ALL (SELECT count(*) as contributions, user_name from relations where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d') + " 00:00:00' GROUP BY user_name)) SELECT SUM(contributions) as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions) "])

	for a in contribs_per_user:
		dict_user_total_contribs[a[1]] = a[0]


	creates_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d')+" 00:00:00' AND version = 1 GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d') + " 00:00:00' AND version = 1 GROUP BY user_name) UNION ALL (SELECT count(*) as contributions, user_name from relations where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d') + " 00:00:00' AND version = 1 GROUP BY user_name)) SELECT SUM(contributions) as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions) "])

	for a in creates_per_user:
		dict_user_creates[a[1]] = a[0]

	#calculate expected ratio for each user over period given as input
	dict_user_expected_ratio = {}
	for k, v in dict_user_total_contribs.items():
		dict_user_expected_ratio[k] = dict_user_creates.get(k,decimal.Decimal(0.0)) / dict_user_total_contribs[k] / diff_expected_user

	#actual ratio per user for the period given as input 
	contribs_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at <= '" + date_after.strftime('%Y-%m-%d') + "' AND created_at > '" + event_date.strftime('%Y-%m-%d')+" 24:00:00' GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at <= '" + date_after.strftime('%Y-%m-%d') + "' AND created_at > '" + event_date.strftime('%Y-%m-%d') + " 24:00:00' GROUP BY user_name) UNION ALL (SELECT count(*) as contributions, user_name from relations where created_at <= '" + date_after.strftime('%Y-%m-%d') + "' AND created_at > '" + event_date.strftime('%Y-%m-%d') + " 24:00:00' GROUP BY user_name)) SELECT SUM(contributions) as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions) "])

	for a in contribs_per_user:
		dict_user_total_contribs[a[1]] = a[0]


	creates_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at <= '" + date_after.strftime('%Y-%m-%d') + "' AND created_at > '" + event_date.strftime('%Y-%m-%d')+" 24:00:00' GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at <= '" + date_after.strftime('%Y-%m-%d') + "' AND created_at > '" + event_date.strftime('%Y-%m-%d') + " 24:00:00' GROUP BY user_name) UNION ALL (SELECT count(*) as contributions, user_name from relations where created_at <= '" + date_after.strftime('%Y-%m-%d') + "' AND created_at > '" + event_date.strftime('%Y-%m-%d') + " 24:00:00' GROUP BY user_name)) SELECT SUM(contributions) as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions) "])

	for a in creates_per_user:
		dict_user_creates[a[1]] = a[0]

	#calculate actual ratio for each user over period given as input
	dict_user_actual_ratio = {}
	for k, v in dict_user_total_contribs.items():
		dict_user_actual_ratio[k] = dict_user_creates.get(k,decimal.Decimal(0.0)) / dict_user_total_contribs[k] / diff_actual_user

	abnormal_return_per_group = [[],[],[],[],[]]
	group_num = 0
	for group in groups:
		for user in group:
			abnormal_return_per_group[group_num].append(dict_user_actual_ratio[user]-dict_user_expected_ratio[user])
		group_num += 1

	group_1 = go.Box(
    	y=trim_95Perc_rule(abnormal_return_per_group[0]),
    	name = 'Group 1',
    	boxpoints = False,
	)
	group_2 = go.Box(
    	y=trim_95Perc_rule(abnormal_return_per_group[1]),
    	name = 'Group 2',
    	boxpoints = False,
	)
	group_3 = go.Box(
    	y=trim_95Perc_rule(abnormal_return_per_group[2]),
    	name = 'Group 3',
    	boxpoints = False,
	)
	group_4 = go.Box(
    	y=trim_95Perc_rule(abnormal_return_per_group[3]),
    	name = 'Group 4',
    	boxpoints = False,
	)
	group_5 = go.Box(
    	y=trim_95Perc_rule(abnormal_return_per_group[4]),
    	name = 'Group 5',
    	boxpoints = False,
	)

	# find max and min for ranges in layout
	maxVal = 0
	minVal = 0
	for data in abnormal_return_per_group:
		if np.amax(data) > maxVal:
			maxVal = np.amax(data)
		if np.amin(data) < minVal:
			minVal = np.amin(data)

	layout = go.Layout(
		title = "Abnormal Return of Maintenance Ratios " +str(diff_actual_user) + " weeks after event",
	    width=1200, height=540,
	    yaxis = dict(range = [minVal,maxVal]),

	)

	data = [group_1,group_2,group_3,group_4,group_5]
	fig = dict(data = data, layout = layout)

	# py.plot(data,filename='box-plots osm London month')
	filelocation = dir_write_to['local']+'/abnormalReturnMaintenance'+str(diff_actual_user)+'weeksAfer.png'
	py.image.save_as(fig,filename = filelocation)

	# UPLOAD TO GOOGLE DRIVE
	filename = 'abnormalReturnMaintenance'+str(diff_actual_user)+'.png'
	googleDriveConnection.upload_GoogleDrive(filename,filelocation, dir_write_to['google'], 'photo/png')

	# ==== SET UP FOR JSON
	filename = "abnormalReturnMaintenance-"+str(diff_actual_user)+"weekAfter"+".json"
	filelocation = dir_write_to['local']+"/"+filename

	# == CHANGE DECIMAL OBJECTS TO FLOAT DATA POINTS
	for data in abnormal_return_per_group:
		for i in range(0,len(data)):
			data[i] = float(data[i])
	json_info = { "data " : abnormal_return_per_group}

	#====MAKE JSON======
	with open(filelocation, "w") as f:
		json.dump(json_info, f)

	# UPLOAD TO GOOGLE DRIVE
	googleDriveConnection.upload_GoogleDrive(filename,filelocation, dir_write_to['google'], 'text/json')




	    

#=========================================================================================#
#===Looking at evolution of the most edited amenity types per user for a certain period===#
#=========================================================================================#
def top_amenity_evolution_per_group(db,googleDriveConnection, date_before,event_date,date_after, iMport, x=None, y=None, import_dir =''):

	#Dates computations
	

	where_clause = ' '
	if x!=None and y!=None and len(x) == 2 and len(y) == 2:
		where_clause += 'AND latitude > '+str(x[1])+' AND longitude > '+str(x[0])+' AND latitude < '+str(y[1])+' AND longitude < '+str(y[0])

	amenity_type_per_user_before_nodes= " SELECT json_agg(tags) as tags, user_name FROM nodes WHERE created_at >= '" + date_before.strftime('%Y-%m-%d') +"' AND created_at < '" + event_date.strftime('%Y-%m-%d')+" 24:00:00'"+ where_clause + " GROUP BY user_name"

	amenity_type_per_user_after_nodes = " SELECT json_agg(tags) as tags, user_name FROM nodes WHERE created_at < '" + date_after.strftime('%Y-%m-%d') +"' AND created_at > '" + event_date.strftime('%Y-%m-%d')+" 00:00:00'"+ where_clause + " GROUP BY user_name"

	amenity_type_per_user_before_ways= " SELECT json_agg(tags) as tags, user_name FROM ways WHERE created_at >= '" + date_before.strftime('%Y-%m-%d') +"' AND created_at < '" + event_date.strftime('%Y-%m-%d')+" 24:00:00' GROUP BY user_name"

	amenity_type_per_user_after_ways = " SELECT json_agg(tags) as tags, user_name FROM ways WHERE created_at < '" + date_after.strftime('%Y-%m-%d') +"' AND created_at > '" + event_date.strftime('%Y-%m-%d')+" 00:00:00' GROUP BY user_name"

	amenity_type_per_user_before_all = "SELECT json_agg(result.tags) as tags, result.user_name FROM (" + amenity_type_per_user_before_nodes + " UNION ALL " + amenity_type_per_user_before_ways+") AS result GROUP BY result.user_name"

	amenity_type_per_user_after_all = "SELECT json_agg(result.tags) as tags, result.user_name FROM (" + amenity_type_per_user_after_nodes + " UNION ALL " + amenity_type_per_user_after_ways+") AS result GROUP BY result.user_name"

	analysis_before = db.execute([amenity_type_per_user_before_all])
	analysis_after = db.execute([amenity_type_per_user_after_all])



	

	
	





    
	

	refDict = build_dictionary_of_amenities()  
	forbiddenEntries = {"yes", "no", "FIXME", "2", "s", "w", "name", "1", "4", "unclassified", "-1"}
	absol_dict = get_amenities_top(db, iMport)
	groups = group_analyser(db, date_before, event_date, x, y)
	

	top1 = list(absol_dict)[2]
	top2 = list(absol_dict)[1]
	top3 = list(absol_dict)[0]
	dict_top = {top1, top2, top3}
	


#=====================Before the import====================================


	dict_top1={}
	dict_top2={}
	dict_top3={}
	dict_top4={}
	dict_top5={}
	
	dict1 = {}
	dict2 = {}
	dict3 = {}
	dict4 = {}
	dict5 = {}

	dict_top12={}
	dict_top22={}
	dict_top32={}
	dict_top42={}
	dict_top52={}
	
	dict12 = {}
	dict22 = {}
	dict32 = {}
	dict42 = {}
	dict52 = {}


	for fields in analysis_before:
		if fields[1] in groups[0]:
			for tag in fields[0]:
					for data in tag:
						for detail in data: 
							if data[detail] in dict_top and data[detail] not in forbiddenEntries:
								if data[detail] in dict_top1:
									dict_top1[data[detail]]+=1
								else:
									dict_top1[data[detail]] =1
							if data[detail] in refDict and data[detail] not in forbiddenEntries: 
								if data[detail] in dict1: 
									dict1[data[detail]]+=1
								else: 
									dict1[data[detail]] =1
		if fields[1] in groups[1]:
			for tag in fields[0]:
					for data in tag:
						for detail in data: 
							if data[detail] in dict_top and data[detail] not in forbiddenEntries:
								if data[detail] in dict_top2:
									dict_top2[data[detail]]+=1
								else:
									dict_top2[data[detail]] =1
							if data[detail] in refDict and data[detail] not in forbiddenEntries: 
								if data[detail] in dict2: 
									dict2[data[detail]]+=1
								else: 
									dict2[data[detail]] =1
		if fields[1] in groups[2]:
			for tag in fields[0]:
					for data in tag:
						for detail in data: 
							if data[detail] in dict_top and data[detail] not in forbiddenEntries:
								if data[detail] in dict_top3:
									dict_top3[data[detail]]+=1
								else:
									dict_top3[data[detail]] =1
							if data[detail] in refDict and data[detail] not in forbiddenEntries: 
								if data[detail] in dict3: 
									dict3[data[detail]]+=1
								else: 
									dict3[data[detail]] =1
		if fields[1] in groups[3]:
			for tag in fields[0]:
					for data in tag:
						for detail in data: 
							if data[detail] in dict_top and data[detail] not in forbiddenEntries:
								if data[detail] in dict_top4:
									dict_top4[data[detail]]+=1
								else:
									dict_top4[data[detail]] =1
							if data[detail] in refDict and data[detail] not in forbiddenEntries: 
								if data[detail] in dict4: 
									dict4[data[detail]]+=1
								else: 
									dict4[data[detail]] =1
		if fields[1] in groups[4]:
			for tag in fields[0]:
					for data in tag:
						for detail in data: 
							if data[detail] in dict_top and data[detail] not in forbiddenEntries:
								if data[detail] in dict_top5:
									dict_top5[data[detail]]+=1
								else:
									dict_top5[data[detail]] =1
							if data[detail] in refDict and data[detail] not in forbiddenEntries: 
								if data[detail] in dict5: 
									dict5[data[detail]]+=1
								else: 
									dict5[data[detail]] =1



		for fields in analysis_after:
			if fields[1] in groups[0]:
				for tag in fields[0]:
						for data in tag:
							for detail in data: 
								if data[detail] in dict_top and data[detail] not in forbiddenEntries:
									if data[detail] in dict_top12:
										dict_top12[data[detail]]+=1
									else:
										dict_top12[data[detail]] =1
								if data[detail] in refDict and data[detail] not in forbiddenEntries: 
									if data[detail] in dict12: 
										dict12[data[detail]]+=1
									else: 
										dict12[data[detail]] =1
			if fields[1] in groups[1]:
				for tag in fields[0]:
						for data in tag:
							for detail in data: 
								if data[detail] in dict_top and data[detail] not in forbiddenEntries:
									if data[detail] in dict_top22:
										dict_top22[data[detail]]+=1
									else:
										dict_top22[data[detail]] =1
								if data[detail] in refDict and data[detail] not in forbiddenEntries: 
									if data[detail] in dict22: 
										dict22[data[detail]]+=1
									else: 
										dict22[data[detail]] =1
			if fields[1] in groups[2]:
				for tag in fields[0]:
						for data in tag:
							for detail in data: 
								if data[detail] in dict_top and data[detail] not in forbiddenEntries:
									if data[detail] in dict_top32:
										dict_top32[data[detail]]+=1
									else:
										dict_top32[data[detail]] =1
								if data[detail] in refDict and data[detail] not in forbiddenEntries: 
									if data[detail] in dict32: 
										dict32[data[detail]]+=1
									else: 
										dict32[data[detail]] =1
			if fields[1] in groups[3]:
				for tag in fields[0]:
						for data in tag:
							for detail in data: 
								if data[detail] in dict_top and data[detail] not in forbiddenEntries:
									if data[detail] in dict_top42:
										dict_top42[data[detail]]+=1
									else:
										dict_top42[data[detail]] =1
								if data[detail] in refDict and data[detail] not in forbiddenEntries: 
									if data[detail] in dict42: 
										dict42[data[detail]]+=1
									else: 
										dict42[data[detail]] =1
			if fields[1] in groups[4]:
				for tag in fields[0]:
						for data in tag:
							for detail in data: 
								if data[detail] in dict_top and data[detail] not in forbiddenEntries:
									if data[detail] in dict_top52:
										dict_top52[data[detail]]+=1
									else:
										dict_top52[data[detail]] =1
								if data[detail] in refDict and data[detail] not in forbiddenEntries: 
									if data[detail] in dict52: 
										dict52[data[detail]]+=1
									else: 
										dict52[data[detail]] =1





	sorted_dict1 = sorted(dict1.items(), key=operator.itemgetter(1))
	sorted_dict2 = sorted(dict2.items(), key=operator.itemgetter(1))
	sorted_dict3 = sorted(dict3.items(), key=operator.itemgetter(1))
	sorted_dict4 = sorted(dict4.items(), key=operator.itemgetter(1))
	sorted_dict5 = sorted(dict5.items(), key=operator.itemgetter(1))


	sorted_dict12 = sorted(dict12.items(), key=operator.itemgetter(1))
	sorted_dict22 = sorted(dict22.items(), key=operator.itemgetter(1))
	sorted_dict32 = sorted(dict32.items(), key=operator.itemgetter(1))
	sorted_dict42 = sorted(dict42.items(), key=operator.itemgetter(1))
	sorted_dict52 = sorted(dict52.items(), key=operator.itemgetter(1))

	total1=0
	total2=0
	total3=0
	total4=0
	total5=0


	total12=0
	total22=0
	total32=0
	total42=0
	total52=0

	for i in range (0, len(sorted_dict1)-1):
		total1+=sorted_dict1[i][1]
	for i in range (0, len(sorted_dict2)-1):
		total2+=sorted_dict2[i][1]
	for i in range (0, len(sorted_dict3)-1):
		total3+=sorted_dict3[i][1]
	for i in range (0, len(sorted_dict4)-1):
		total4+=sorted_dict4[i][1]
	for i in range (0, len(sorted_dict5)-1):
		total5+=sorted_dict5[i][1]


	if total1 ==0:
		total1=1
	if total2 ==0:
		total2=1
	if total3 ==0:
		total3=1
	if total4 ==0:
		total4=1
	if total5 ==0:
		total5=1
	


	for i in range (0, len(sorted_dict12)-1):
		total12+=sorted_dict12[i][1]
	for i in range (0, len(sorted_dict22)-1):
		total22+=sorted_dict22[i][1]
	for i in range (0, len(sorted_dict32)-1):
		total32+=sorted_dict32[i][1]
	for i in range (0, len(sorted_dict42)-1):
		total42+=sorted_dict42[i][1]
	for i in range (0, len(sorted_dict52)-1):
		total52+=sorted_dict52[i][1]

	if total12 ==0:
		total12=1
	if total22 ==0:
		total22=1
	if total32 ==0:
		total32=1
	if total42 ==0:
		total42=1
	if total52 ==0:
		total52=1
	


	for i in dict_top:
		if i not in dict_top1:
			dict_top1[i]=0
		if i not in dict_top2:
			dict_top2[i]=0
		if i not in dict_top3:
			dict_top3[i]=0
		if i not in dict_top4:
			dict_top4[i]=0
		if i not in dict_top5:
			dict_top5[i]=0
		if i not in dict_top12:
			dict_top12[i]=0
		if i not in dict_top22:
			dict_top22[i]=0
		if i not in dict_top32:
			dict_top32[i]=0
		if i not in dict_top42:
			dict_top42[i]=0
		if i not in dict_top52:
			dict_top52[i]=0
	



  ##plot the top edited amenities for each group before the import



	trace_top1 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[dict_top1[top1]/total1, dict_top2[top1]/total2, dict_top3[top1]/total3, dict_top4[top1]/total4, dict_top5[top1]/total5], name='#1:' + top1, text=[dict_top1[top1], dict_top2[top1], dict_top3[top1], dict_top4[top1], dict_top5[top1]])
	trace_top2 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[dict_top1[top2]/total1, dict_top2[top2]/total2, dict_top3[top2]/total3, dict_top4[top2]/total4, dict_top5[top2]/total5], name='#2:' + top2, text=[dict_top1[top2], dict_top2[top2], dict_top3[top2], dict_top4[top2], dict_top5[top2]])
	trace_top3 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[dict_top1[top3]/total1, dict_top2[top3]/total2, dict_top3[top3]/total3, dict_top4[top3]/total4, dict_top5[top3]/total5], name='#3:' + top3, text=[dict_top1[top3], dict_top2[top3], dict_top3[top3], dict_top4[top3], dict_top5[top3]])


	data = [trace_top1, trace_top2, trace_top3]
	layout = go.Layout(barmode='group')
	fig = go.Figure(data=data, layout=layout)
	


 ###plot the ratio of editing of the top amenities edited by the import



	trace_before1 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[sorted_dict1[len(sorted_dict1)-1][1]/total1, sorted_dict2[len(sorted_dict2)-1][1]/total2, sorted_dict3[len(sorted_dict3)-1][1]/total3, sorted_dict4[len(sorted_dict4)-1][1]/total4, sorted_dict5[len(sorted_dict5)-1][1]/total5], name='#1', text=[sorted_dict1[len(sorted_dict1)-1][0], sorted_dict2[len(sorted_dict2)-1][0], sorted_dict3[len(sorted_dict3)-1][0], sorted_dict4[len(sorted_dict4)-1][0], sorted_dict5[len(sorted_dict5)-1][0]])
	trace_before2 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[sorted_dict1[len(sorted_dict1)-2][1]/total1, sorted_dict2[len(sorted_dict2)-2][1]/total2, sorted_dict3[len(sorted_dict3)-2][1]/total3, sorted_dict4[len(sorted_dict4)-2][1]/total4, sorted_dict5[len(sorted_dict5)-2][1]/total5], name='#2',text=[sorted_dict1[len(sorted_dict1)-2][0], sorted_dict2[len(sorted_dict2)-2][0], sorted_dict3[len(sorted_dict3)-2][0], sorted_dict4[len(sorted_dict4)-2][0], sorted_dict5[len(sorted_dict5)-2][0]])
	trace_before3 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[sorted_dict1[len(sorted_dict1)-3][1]/total1, sorted_dict2[len(sorted_dict2)-3][1]/total2, sorted_dict3[len(sorted_dict3)-3][1]/total3, sorted_dict4[len(sorted_dict4)-3][1]/total4, sorted_dict5[len(sorted_dict5)-3][1]/total5], name='#3', text=[sorted_dict1[len(sorted_dict1)-3][0], sorted_dict2[len(sorted_dict2)-3][0], sorted_dict3[len(sorted_dict3)-3][0], sorted_dict4[len(sorted_dict4)-3][0], sorted_dict5[len(sorted_dict5)-3][0]])

	data1 = [trace_before1, trace_before2, trace_before3]
	layout1 = go.Layout(barmode='group')
	fig1 = go.Figure(data=data1, layout=layout1)
	



 ###plot the top edited amenities for each group after the import

	trace_top12 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[dict_top12[top1]/total12, dict_top22[top1]/total22, dict_top32[top1]/total32, dict_top42[top1]/total42, dict_top52[top1]/total52], name='#1:' + top1, text=[dict_top12[top1], dict_top22[top1], dict_top32[top1], dict_top42[top1], dict_top52[top1]])
	trace_top22 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[dict_top12[top2]/total12, dict_top22[top2]/total22, dict_top32[top2]/total32, dict_top42[top2]/total42, dict_top52[top2]/total52], name='#2:' + top2, text=[dict_top12[top2], dict_top22[top2], dict_top32[top2], dict_top42[top2], dict_top52[top2]])
	trace_top32 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[dict_top12[top3]/total12, dict_top22[top3]/total22, dict_top32[top3]/total32, dict_top42[top3]/total42, dict_top52[top3]/total52], name='#3:' + top3, text=[dict_top12[top3], dict_top22[top3], dict_top32[top3], dict_top42[top3], dict_top52[top3]])


	data2 = [trace_top12, trace_top22, trace_top32]
	layout2 = go.Layout(barmode='group')
	fig2 = go.Figure(data=data2, layout=layout2)
	

 ###plot the ratio of editing of the top amenities edited by the import

	trace_after1 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[sorted_dict12[len(sorted_dict12)-1][1]/total12, sorted_dict22[len(sorted_dict22)-1][1]/total22, sorted_dict32[len(sorted_dict32)-1][1]/total32, sorted_dict42[len(sorted_dict42)-1][1]/total42, sorted_dict52[len(sorted_dict52)-1][1]/total52], name='#1', text=[sorted_dict12[len(sorted_dict12)-1][0], sorted_dict22[len(sorted_dict22)-1][0], sorted_dict32[len(sorted_dict32)-1][0], sorted_dict42[len(sorted_dict42)-1][0], sorted_dict52[len(sorted_dict52)-1][0]])
	trace_after2 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[sorted_dict12[len(sorted_dict12)-2][1]/total12, sorted_dict22[len(sorted_dict22)-2][1]/total22, sorted_dict32[len(sorted_dict32)-2][1]/total32, sorted_dict42[len(sorted_dict42)-2][1]/total42, sorted_dict52[len(sorted_dict52)-2][1]/total52], name='#2', text=[sorted_dict12[len(sorted_dict12)-2][0], sorted_dict22[len(sorted_dict22)-2][0], sorted_dict32[len(sorted_dict32)-2][0], sorted_dict42[len(sorted_dict42)-2][0], sorted_dict52[len(sorted_dict52)-2][0]])
	trace_after3 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[sorted_dict12[len(sorted_dict12)-3][1]/total12, sorted_dict22[len(sorted_dict22)-3][1]/total22, sorted_dict32[len(sorted_dict32)-3][1]/total32, sorted_dict42[len(sorted_dict42)-3][1]/total42, sorted_dict52[len(sorted_dict52)-3][1]/total52], name='#3', text=[sorted_dict12[len(sorted_dict12)-3][0], sorted_dict22[len(sorted_dict22)-3][0], sorted_dict32[len(sorted_dict32)-3][0], sorted_dict42[len(sorted_dict42)-3][0], sorted_dict52[len(sorted_dict52)-3][0]])

	data3 = [trace_after1, trace_after2, trace_after3]
	layout3 = go.Layout(barmode='group')
	fig3 = go.Figure(data=data3, layout=layout3)







	# # SAVE LOCALLY
	# py.image.save_as(fig, filename=dir_write_to['local']+'/top_amenity_focus_before'+date_convert.strftime('%Y-%m-%d')+'.png')

	# # UPLOAD TO GOOGLE DRIVE
	# filename = 'top_amenity_focus_before'+date_convert.strftime('%Y-%m-%d')+'.png'
	# filelocation = dir_write_to['local']+'/top_amenity_focus_before'+date_convert.strftime('%Y-%m-%d')+'.png'
	# googleDriveConnection.upload_GoogleDrive(filename,filelocation, dir_write_to['google'])


	# # SAVE LOCALLY
	# py.image.save_as(fig1, filename=dir_write_to['local']+'/top_amenity_focus_after'+date_convert.strftime('%Y-%m-%d')+'.png')

	# # UPLOAD TO GOOGLE DRIVE
	# filename = 'top_amenity_focus_after'+date_convert.strftime('%Y-%m-%d')+'.png'
	# filelocation = dir_write_to['local']+'/top_amenity_focus_after'+date_convert.strftime('%Y-%m-%d')+'.png'
	# googleDriveConnection.upload_GoogleDrive(filename,filelocation, dir_write_to['google'])

	# # SAVE LOCALLY
	# py.image.save_as(fig2, filename=dir_write_to['local']+'/top_import_amenity_before'+date_convert.strftime('%Y-%m-%d')+'.png')

	# # UPLOAD TO GOOGLE DRIVE
	# filename = 'top_import_amenity_before'+date_convert.strftime('%Y-%m-%d')+'.png'
	# filelocation = dir_write_to['local']+'/top_import_amenity_before'+date_convert.strftime('%Y-%m-%d')+'.png'
	# googleDriveConnection.upload_GoogleDrive(filename,filelocation, dir_write_to['google'])

	# # SAVE LOCALLY
	# py.image.save_as(fig3, filename=dir_write_to['local']+'/top_import_amenity_after'+date_convert.strftime('%Y-%m-%d')+'.png')

	# # UPLOAD TO GOOGLE DRIVE
	# filename = 'top_import_amenity_after'+date_convert.strftime('%Y-%m-%d')+'.png'
	# filelocation = dir_write_to['local']+'/top_import_amenity_after'+date_convert.strftime('%Y-%m-%d')+'.png'
	# googleDriveConnection.upload_GoogleDrive(filename,filelocation, dir_write_to['google'])











#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------
#HELPER FUNCTIONS
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------

#===================================================================================================================
#=========DETECTS THE ABSOLUTE TOP 3 OF MOST EDITED AMENITIES AMONG NODES, WAYS AND RELATIONS OF AN IMPORT=========
#===================================================================================================================

def get_amenities_top(db, iMport=[]):

	top = []
	for i in range(1, len(iMport)):
		for element in iMport[i]:
			top.append(element)


	forbiddenEntries = {"yes", "no", "FIXME", "2", "s", "w", "name", "1", "4", "unclassified", "-1"}
	dict_top = {}

	for i in top:
		for elements in i: 
			if elements not in dict_top and elements not in forbiddenEntries:
				dict_top[elements] = i[elements]

	if len(dict_top)==2:
		dict_top["not provided"]=0
	if len(dict_top)==1:
		dict_top["not provided1"]=0
		dict_top["not provided2"]=0




	absol_dict = dict(sorted(dict_top.items(), key=operator.itemgetter(1), reverse=True)[:3])

	


	return absol_dict




#================================================================================
#=========COMPUTES THE GROUPS AND RETURNS AN ARRAY OF ARRAY OF USERNAMES=========
#================================================================================
def group_analyser(db, date_before, event_date , x = None, y = None):

	# If there is a location restriction
	where_clause = ' '
	if x!=None and y!=None and len(x) == 2 and len(y) == 2:
		where_clause += 'AND latitude > '+str(x[1])+' AND longitude > '+str(x[0])+' AND latitude < '+str(y[1])+' AND longitude < '+str(y[0])


	#The number of weeks between event date and the date before the event

	#Average number of edits per user per week for the six months before
  	#This query is location proof
	expected_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d')+"'"+ where_clause + " GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d') + "' GROUP BY user_name) UNION ALL (SELECT count(*) as contributions, user_name from relations where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d') + "' GROUP BY user_name)) SELECT SUM(contributions) as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions)"])

	# a[0]: nb contrib/semaine
	# a[1]: user

	# Divides the expected user in 5 groups
	groups = [[],[],[],[],[]]

	for a in expected_per_user:
		if a[0] > 0.0 and a[0] < 10.0:
			groups[0].append(a[1])
		if a[0] > 10.0 and a[0] < 100.0:
			groups[1].append(a[1])
		if a[0] > 100.0 and a[0] < 1000.0:
			groups[2].append(a[1])
		if a[0] > 1000.0 and a[0] < 10000.0:
			groups[3].append(a[1])
		if a[0] > 10000.0:
			groups[4].append(a[1])

	return groups

def group_analyserv2(db, date_before, event_date , x = None, y = None):
	# If there is a location restriction
	where_clause = ' '
	if x!=None and y!=None and len(x) == 2 and len(y) == 2:
		where_clause += 'AND latitude > '+str(x[1])+' AND longitude > '+str(x[0])+' AND latitude < '+str(y[1])+' AND longitude < '+str(y[0])


	#The number of weeks between event date and the date before the event

	#Average number of edits per user per week for the six months before
  	#This query is location proof
	expected_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d')+"'"+ where_clause + " GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d') + "' GROUP BY user_name) UNION ALL (SELECT count(*) as contributions, user_name from relations where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d') + "' GROUP BY user_name)) SELECT SUM(contributions) as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions)"])

	# a[0]: nb contrib/semaine
	# a[1]: user

	# Divides the expected user in 5 groups
	groups = [[],[],[],[],[]]

	total_contributions = 0
	total_user = 0
	for a in expected_per_user:
		total_contributions += a[0]
		total_user +=1

	threshold = []
	diff = total_contributions /5

	# By even thresholds
	# for x in range(0,5):
	# 	if x == 4:
	# 		threshold.append(total_contributions)
	# 		break
	# 	threshold.append(diff*(x+1))

	# ========BY percentage =============
	threshold.append(decimal.Decimal(0.1)*total_contributions)
	threshold.append(decimal.Decimal(0.25)*total_contributions)
	threshold.append(decimal.Decimal(0.45)*total_contributions)
	threshold.append(decimal.Decimal(0.70)*total_contributions)
	threshold.append(total_contributions)

	expected_per_user.sort(key= lambda x : int (x[0]))

	current_sum = 0
	for a in expected_per_user:
		current_sum += a[0]
		for index in range(0,5):
			if current_sum <= threshold[index]:
				groups[index].append(a[1])
				break

	total_2 = 0
	for group in groups:
		for user in group:
			total_2 += 1
		print(total_2)
		total_2 = 0
		print(group[total_2-1])

	return groups

#================================================================================================
#=========Trips a list and returns a list with the bottom 2% remove and upper 2% removed=========
#================================================================================================
def trim_95Perc_rule(data):

	size_of_list = len(data)

	if size_of_list < 10:
		return data

	std_dev = np.std(data)
	mean = np.mean(data)

	factor = 2
	false_positive = []
	for num in data:
		if not abs(num - mean) <= (factor * std_dev):
			data.remove(num)
			false_positive.append(num)

	# print("Disregarded Data Points: ")
	# print(false_positive)
			
	return data


#================================================================================================
#================================RANGE FINDER====================================================
#================================================================================================
def find_range(data):

	return [np.min(data),np.max(data)]

	















