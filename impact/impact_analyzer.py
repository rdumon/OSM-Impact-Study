import sys
import json
import decimal
from datetime import datetime
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import operator
import numpy as np
plotly.tools.set_credentials_file(username='aoussbai', api_key='uWPqQZwnbe5MgCrfqk3V')

sys.path.insert(0, '../lib/')
# from db import DB




#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
#SET OF VARIABLES AND FUNCTIONS USEFUL TO LOOK AT AMENITIES
#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------


def build_dictionary_of_amenities(data):

	dictionary_amenities = {} 

	for object in data["data"]:
		dictionary_amenities[object["value"]] = 0

	return dictionary_amenities






#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------
#ANALYSING FUNCTIONS
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------

#==================================================================================
#=========All dates should have the format 'YearMonthDate' i.e. '20090311'=========
#==================================================================================
def abnormal_return_for_group(db, groups, date_before, event_date , date_after, x = None, y = None):

	# If there is a location restriction
	where_clause = ' '
	if x!=None and y!=None and len(x) == 2 and len(y) == 2:
		where_clause += 'AND latitude > '+str(x[1])+' AND longitude > '+str(x[0])+' AND latitude < '+str(y[1])+' AND longitude < '+str(y[0])

	#Dates computations
	event_date_convert = datetime.strptime(event_date,'%Y%m%d')
	date_before_convert = datetime.strptime(date_before,'%Y%m%d')
	date_after_convert = datetime.strptime(date_after,'%Y%m%d')

	#The number of weeks between event date and the date before the event
	diff_expected_user = (event_date_convert - date_before_convert).days /7
	#The number of weeks between event date and the date after the event
	diff_actual_user = (date_after_convert - event_date_convert).days /7

	#Average number of edits per user per week for the six months before
  	#This query is location proof
	expected_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d')+"'"+ where_clause + " GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d') + "' GROUP BY user_name) UNION ALL (SELECT count(*) as contributions, user_name from relations where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d') + "' GROUP BY user_name)) SELECT (SUM(contributions)/"+str(diff_expected_user)+") as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions)"])

	expected = {}

	for a in expected_per_user:
		expected[a[1]] = a[0]

	#query average contribution for each user in each group
	actual_one_month = {}
	actual_per_user_one_month = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at > '" + event_date_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + date_after_convert.strftime('%Y-%m-%d') +"'"+ where_clause + " GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at > '" + event_date_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + date_after_convert.strftime('%Y-%m-%d') + "' GROUP BY user_name) UNION ALL (SELECT count(*) as contributions, user_name from relations where created_at > '" + event_date_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + date_after_convert.strftime('%Y-%m-%d') + "' GROUP BY user_name)) SELECT (SUM(contributions)/"+str(diff_actual_user)+") as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions)"])
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
    	y=trim_95Perc_rule(dataAbnormal[0]),
    	name = 'Group 1',
    	boxpoints = False,
	)
	group_2 = go.Box(
    	y=trim_95Perc_rule(dataAbnormal[1]),
    	name = 'Group 2',
    	boxpoints = False,
	)
	group_3 = go.Box(
    	y=trim_95Perc_rule(dataAbnormal[2]),
    	name = 'Group 3',
    	boxpoints = False,
	)
	group_4 = go.Box(
    	y=trim_95Perc_rule(dataAbnormal[3]),
    	name = 'Group 4',
    	boxpoints = False,
	)
	group_5 = go.Box(
    	y=trim_95Perc_rule(dataAbnormal[4]),
    	name = 'Group 5',
    	boxpoints = False,
	)

	data = [group_1,group_2,group_3,group_4,group_5]
	py.plot(data,filename='box-plots osm London 3 month')

#=================================================================================================
#=========Looking at evolution of deletes/creation and edits per day for a certain period=========
#=================================================================================================
def contribution_types_gobal_analysis(db, date_before,event_date,date_after, x=None, y=None):

	#Dates computations
	event_date_convert = datetime.strptime(event_date,'%Y%m%d')
	date_before_convert = datetime.strptime(date_before,'%Y%m%d')
	date_after_convert = datetime.strptime(date_after,'%Y%m%d')

	#work out evolution of delete contributions
	delete_per_day = db.execute(["with C as((SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM nodes WHERE  created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after_convert.strftime('%Y-%m-%d')+"'"+ " AND deleted = true GROUP BY created_at) UNION ALL (SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM ways WHERE  created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after_convert.strftime('%Y-%m-%d')+"'"+ " AND deleted = true GROUP BY created_at) UNION ALL (SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM relations WHERE  created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after_convert.strftime('%Y-%m-%d')+"'"+ " AND deleted = true GROUP BY created_at)) SELECT created_at,SUM(contrib_deletion) as sum_contrib_deletion FROM C GROUP BY created_at ORDER BY created_at" ])

	delete_per_day_x = []
	delete_per_day_y = []
	for a in delete_per_day:
		delete_per_day_x.append((datetime.strptime(a[0],'%Y%m%d')).strftime('%Y-%m-%d'))
		delete_per_day_y.append(a[1])


	#work out evolution of creation contributions
	creation_per_day = db.execute(["with C as((SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM nodes WHERE  created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after_convert.strftime('%Y-%m-%d')+"'"+ " AND version = 1 GROUP BY created_at) UNION ALL (SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM ways WHERE  created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after_convert.strftime('%Y-%m-%d')+"'"+ " AND version = 1 GROUP BY created_at) UNION ALL (SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM relations WHERE  created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after_convert.strftime('%Y-%m-%d')+"'"+ " AND version = 1 GROUP BY created_at)) SELECT created_at,SUM(contrib_deletion) as sum_contrib_deletion FROM C GROUP BY created_at ORDER BY created_at" ])

	creation_per_day_x = []
	creation_per_day_y = []
	for a in creation_per_day:
		creation_per_day_x.append((datetime.strptime(a[0],'%Y%m%d')).strftime('%Y-%m-%d'))
		creation_per_day_y.append(a[1])

	# #work out evolution of edits contributions
	edits_per_day = db.execute(["with C as((SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM nodes WHERE  created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after_convert.strftime('%Y-%m-%d')+"'"+ " AND deleted = false AND version != 1 GROUP BY created_at) UNION ALL (SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM ways WHERE  created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after_convert.strftime('%Y-%m-%d')+"'"+ " AND deleted = false AND version != 1 GROUP BY created_at) UNION ALL (SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM relations WHERE  created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after_convert.strftime('%Y-%m-%d')+"'"+ " AND deleted = false AND version != 1 GROUP BY created_at)) SELECT created_at,SUM(contrib_deletion) as sum_contrib_deletion FROM C GROUP BY created_at ORDER BY created_at" ])

	edits_per_day_x = []
	edits_per_day_y = []
	for a in edits_per_day:
		edits_per_day_x.append((datetime.strptime(a[0],'%Y%m%d')).strftime('%Y-%m-%d'))
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
    x = [event_date_convert.strftime('%Y-%m-%d'),event_date_convert.strftime('%Y-%m-%d')],
    y = [-20,70000],
    mode = 'lines',
    name = 'Day of Import'
	)

	data = [ trace1 ,trace2, trace3, trace4]
	py.plot(data, filename = 'edit_creation_delete for period')

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

    
#-------------------------------------------------------------------------------------
#Looking at evolution of the most edited amenity types per user for a certain period
#-------------------------------------------------------------------------------------
def contribution_amenity_type_analysisv2(db,groups, date_before,event_date,date_after, x=None, y=None):

	#Dates computations
	event_date_convert = datetime.strptime(event_date,'%Y%m%d')
	date_before_convert = datetime.strptime(date_before,'%Y%m%d')
	date_after_convert = datetime.strptime(date_after,'%Y%m%d')

	where_clause = ' '
	if x!=None and y!=None and len(x) == 2 and len(y) == 2:
		where_clause += 'AND latitude > '+str(x[1])+' AND longitude > '+str(x[0])+' AND latitude < '+str(y[1])+' AND longitude < '+str(y[0])


	amenity_type_per_user_before = db.execute([" SELECT json_agg(tags) as tags, user_name FROM nodes WHERE created_at >= '" + date_before_convert.strftime('%Y-%m-%d') +"' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d')+"'"+ where_clause + " GROUP BY user_name"])
	amenity_type_per_user_after = db.execute([" SELECT json_agg(tags) as tags, user_name FROM nodes WHERE created_at < '" + date_after_convert.strftime('%Y-%m-%d') +"' AND created_at > '" + event_date_convert.strftime('%Y-%m-%d')+"'"+ where_clause + " GROUP BY user_name"])
	
	
	with open('/Users/aousssbai/Desktop/OSM-Impact-Study/lib/amenities.json') as data_file:
		data = json.load(data_file)  
	refDict = build_dictionary_of_amenities(data)  
	forbiddenEntries = {"yes", "no", "FIXME", "2", "s", "w"}



	dict1 = {}
	dict2 = {}
	dict3 = {}
	dict4 = {}
	dict5 = {}


	for fields in amenity_type_per_user_before:
		if fields[1] in groups[0]:
			for tag in fields[0]:
					for data in tag:
						if tag[data] in refDict and tag[data] not in forbiddenEntries: 
							if tag[data] in dict1: 
								dict1[tag[data]]+=1
							else: 
								dict1[tag[data]] =1
		if fields[1] in groups[1]:
			for tag in fields[0]:
					for data in tag:
						if tag[data] in refDict and tag[data] not in forbiddenEntries: 
							if tag[data] in dict2: 
								dict2[tag[data]]+=1
							else: 
								dict2[tag[data]] =1
		if fields[1] in groups[2]:
			for tag in fields[0]:
					for data in tag:
						if tag[data] in refDict and tag[data] not in forbiddenEntries: 
							if tag[data] in dict3: 
								dict3[tag[data]]+=1
							else: 
								dict3[tag[data]] =1
		if fields[1] in groups[3]:
			for tag in fields[0]:
					for data in tag:
						if tag[data] in refDict and tag[data] not in forbiddenEntries: 
							if tag[data] in dict4: 
								dict4[tag[data]]+=1
							else: 
								dict4[tag[data]] =1
		if fields[1] in groups[4]:
			for tag in fields[0]:
					for data in tag:
						if tag[data] in refDict and tag[data] not in forbiddenEntries: 
							if tag[data] in dict5: 
								dict5[tag[data]]+=1
							else: 
								dict5[tag[data]] =1

            
		    		



	sorted_dict1 = sorted(dict1.items(), key=operator.itemgetter(1))
	sorted_dict2 = sorted(dict2.items(), key=operator.itemgetter(1))
	sorted_dict3 = sorted(dict3.items(), key=operator.itemgetter(1))
	sorted_dict4 = sorted(dict4.items(), key=operator.itemgetter(1))
	sorted_dict5 = sorted(dict5.items(), key=operator.itemgetter(1))

	total1=0
	total2=0
	total3=0
	total4=0
	total5=0

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



	trace1 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[sorted_dict1[len(sorted_dict1)-1][1]/total1, sorted_dict2[len(sorted_dict2)-1][1]/total2, sorted_dict3[len(sorted_dict3)-1][1]/total3, sorted_dict4[len(sorted_dict4)-1][1]/total4, sorted_dict5[len(sorted_dict5)-1][1]/total5], name='#1', text=[sorted_dict1[len(sorted_dict1)-1][0], sorted_dict2[len(sorted_dict2)-1][0], sorted_dict3[len(sorted_dict3)-1][0], sorted_dict4[len(sorted_dict4)-1][0], sorted_dict5[len(sorted_dict5)-1][0]])

	trace2 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[sorted_dict1[len(sorted_dict1)-2][1]/total1, sorted_dict2[len(sorted_dict2)-2][1]/total2, sorted_dict3[len(sorted_dict3)-2][1]/total3, sorted_dict4[len(sorted_dict4)-2][1]/total4, sorted_dict5[len(sorted_dict5)-2][1]/total5], name='#2',text=[sorted_dict1[len(sorted_dict1)-2][0], sorted_dict2[len(sorted_dict2)-2][0], sorted_dict3[len(sorted_dict3)-2][0], sorted_dict4[len(sorted_dict4)-2][0], sorted_dict5[len(sorted_dict5)-2][0]])

	trace3 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[sorted_dict1[len(sorted_dict1)-3][1]/total1, sorted_dict2[len(sorted_dict2)-3][1]/total2, sorted_dict3[len(sorted_dict3)-3][1]/total3, sorted_dict4[len(sorted_dict4)-3][1]/total4, sorted_dict5[len(sorted_dict5)-3][1]/total5], name='#3', text=[sorted_dict1[len(sorted_dict1)-3][0], sorted_dict2[len(sorted_dict2)-3][0], sorted_dict3[len(sorted_dict3)-3][0], sorted_dict4[len(sorted_dict4)-3][0], sorted_dict5[len(sorted_dict5)-3][0]])

	data = [trace1, trace2, trace3]
	layout = go.Layout(barmode='group')
	fig = go.Figure(data=data, layout=layout)
	py.plot(fig, filename='grouped-bar-before')







	dict12 = {}
	dict22 = {}
	dict32 = {}
	dict42 = {}
	dict52 = {}


	for fields in amenity_type_per_user_after:
		if fields[1] in groups[0]:
			for tag in fields[0]:
					for data in tag:
						if tag[data] in refDict and tag[data] not in forbiddenEntries: 
							if tag[data] in dict12: 
								dict12[tag[data]]+=1
							else: 
								dict12[tag[data]] =1
		if fields[1] in groups[1]:
			for tag in fields[0]:
					for data in tag:
						if tag[data] in refDict and tag[data] not in forbiddenEntries: 
							if tag[data] in dict22: 
								dict22[tag[data]]+=1
							else: 
								dict22[tag[data]] =1
		if fields[1] in groups[2]:
			for tag in fields[0]:
					for data in tag:
						if tag[data] in refDict and tag[data] not in forbiddenEntries: 
							if tag[data] in dict32: 
								dict32[tag[data]]+=1
							else: 
								dict32[tag[data]] =1
		if fields[1] in groups[3]:
			for tag in fields[0]:
					for data in tag:
						if tag[data] in refDict and tag[data] not in forbiddenEntries: 
							if tag[data] in dict42: 
								dict42[tag[data]]+=1
							else: 
								dict42[tag[data]] =1
		if fields[1] in groups[4]:
			for tag in fields[0]:
					for data in tag:
						if tag[data] in refDict and tag[data] not in forbiddenEntries: 
							if tag[data] in dict52: 
								dict52[tag[data]]+=1
							else: 
								dict52[tag[data]] =1

            
		    		



	sorted_dict12 = sorted(dict12.items(), key=operator.itemgetter(1))
	sorted_dict22 = sorted(dict22.items(), key=operator.itemgetter(1))
	sorted_dict32 = sorted(dict32.items(), key=operator.itemgetter(1))
	sorted_dict42 = sorted(dict42.items(), key=operator.itemgetter(1))
	sorted_dict52 = sorted(dict52.items(), key=operator.itemgetter(1))

	total12=0
	total22=0
	total32=0
	total42=0
	total52=0

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



	trace12 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[sorted_dict12[len(sorted_dict12)-1][1]/total12, sorted_dict22[len(sorted_dict22)-1][1]/total22, sorted_dict32[len(sorted_dict32)-1][1]/total32, sorted_dict42[len(sorted_dict42)-1][1]/total42, sorted_dict52[len(sorted_dict52)-1][1]/total52], name='#1', text=[sorted_dict12[len(sorted_dict12)-1][0], sorted_dict22[len(sorted_dict22)-1][0], sorted_dict32[len(sorted_dict32)-1][0], sorted_dict42[len(sorted_dict42)-1][0], sorted_dict52[len(sorted_dict52)-1][0]])

	trace22 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[sorted_dict12[len(sorted_dict12)-2][1]/total12, sorted_dict22[len(sorted_dict22)-2][1]/total22, sorted_dict32[len(sorted_dict32)-2][1]/total32, sorted_dict42[len(sorted_dict42)-2][1]/total42, sorted_dict52[len(sorted_dict52)-2][1]/total52], name='#2',text=[sorted_dict12[len(sorted_dict12)-2][0], sorted_dict22[len(sorted_dict22)-2][0], sorted_dict32[len(sorted_dict32)-2][0], sorted_dict42[len(sorted_dict42)-2][0], sorted_dict52[len(sorted_dict52)-2][0]])

	trace32 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[sorted_dict12[len(sorted_dict12)-3][1]/total12, sorted_dict22[len(sorted_dict22)-3][1]/total22, sorted_dict32[len(sorted_dict32)-3][1]/total32, sorted_dict42[len(sorted_dict42)-3][1]/total42, sorted_dict52[len(sorted_dict52)-3][1]/total52], name='#3', text=[sorted_dict12[len(sorted_dict12)-3][0], sorted_dict22[len(sorted_dict22)-3][0], sorted_dict32[len(sorted_dict32)-3][0], sorted_dict42[len(sorted_dict42)-3][0], sorted_dict52[len(sorted_dict52)-3][0]])

	data2 = [trace12, trace22, trace32]
	layout2 = go.Layout(barmode='group')
	fig2 = go.Figure(data=data2, layout=layout2)
	py.plot(fig2, filename='grouped-bar-after')


#=========================================================================================#
#===Looking at evolution of the most edited amenity types per user for a certain period===#
#=========================================================================================#
def top_amenity_evolution_per_group(db,groups, date_before,event_date,date_after, x=None, y=None):

	#Dates computations
	event_date_convert = datetime.strptime(event_date,'%Y%m%d')
	date_before_convert = datetime.strptime(date_before,'%Y%m%d')
	date_after_convert = datetime.strptime(date_after,'%Y%m%d')

	where_clause = ' '
	if x!=None and y!=None and len(x) == 2 and len(y) == 2:
		where_clause += 'AND latitude > '+str(x[1])+' AND longitude > '+str(x[0])+' AND latitude < '+str(y[1])+' AND longitude < '+str(y[0])


	amenity_type_per_user_before = db.execute([" SELECT json_agg(tags) as tags, user_name FROM nodes WHERE created_at >= '" + date_before_convert.strftime('%Y-%m-%d') +"' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d')+"'"+ where_clause + " GROUP BY user_name"])
	amenity_type_per_user_after = db.execute([" SELECT json_agg(tags) as tags, user_name FROM nodes WHERE created_at < '" + date_after_convert.strftime('%Y-%m-%d') +"' AND created_at > '" + event_date_convert.strftime('%Y-%m-%d')+"'"+ where_clause + " GROUP BY user_name"])
	
	
	with open('/Users/aousssbai/Desktop/OSM-Impact-Study/lib/amenities.json') as data_file:
		data = json.load(data_file)  
	refDict = build_dictionary_of_amenities(data)  
	forbiddenEntries = {"yes", "no", "FIXME", "2", "s", "w", "name"}
	absol_dict = get_amenities_top()
	print(absol_dict)

	top1 = list(absol_dict)[2]
	top2 = list(absol_dict)[1]
	top3 = list(absol_dict)[0]
	dict_top = {top1, top2, top3}

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


	for fields in amenity_type_per_user_after:
		if fields[1] in groups[0]:
			for tag in fields[0]:
					for data in tag:
						if tag[data] in dict_top and tag[data] not in forbiddenEntries:
							if tag[data] in dict_top1:
								dict_top1[tag[data]]+=1
							else:
								dict_top1[tag[data]] =1
						if tag[data] in refDict and tag[data] not in forbiddenEntries: 
							if tag[data] in dict1: 
								dict1[tag[data]]+=1
							else: 
								dict1[tag[data]] =1
		if fields[1] in groups[1]:
			for tag in fields[0]:
					for data in tag:
						if tag[data] in dict_top and tag[data] not in forbiddenEntries:
							if tag[data] in dict_top2:
								dict_top2[tag[data]]+=1
							else:
								dict_top2[tag[data]] =1
						if tag[data] in refDict and tag[data] not in forbiddenEntries: 
							if tag[data] in dict2: 
								dict2[tag[data]]+=1
							else: 
								dict2[tag[data]] =1
		if fields[1] in groups[2]:
			for tag in fields[0]:
					for data in tag:
						if tag[data] in dict_top and tag[data] not in forbiddenEntries:
							if tag[data] in dict_top3:
								dict_top3[tag[data]]+=1
							else:
								dict_top3[tag[data]] =1
						if tag[data] in refDict and tag[data] not in forbiddenEntries: 
							if tag[data] in dict3: 
								dict3[tag[data]]+=1
							else: 
								dict3[tag[data]] =1
		if fields[1] in groups[3]:
			for tag in fields[0]:
					for data in tag:
						if tag[data] in dict_top and tag[data] not in forbiddenEntries:
							if tag[data] in dict_top4:
								dict_top4[tag[data]]+=1
							else:
								dict_top4[tag[data]] =1
						if tag[data] in refDict and tag[data] not in forbiddenEntries: 
							if tag[data] in dict4: 
								dict4[tag[data]]+=1
							else: 
								dict4[tag[data]] =1
		if fields[1] in groups[4]:
			for tag in fields[0]:
					for data in tag:
						if tag[data] in dict_top and tag[data] not in forbiddenEntries:
							if tag[data] in dict_top5:
								dict_top5[tag[data]]+=1
							else:
								dict_top5[tag[data]] =1
						if tag[data] in refDict and tag[data] not in forbiddenEntries: 
							if tag[data] in dict5: 
								dict5[tag[data]]+=1
							else: 
								dict5[tag[data]] =1




	sorted_dict1 = sorted(dict1.items(), key=operator.itemgetter(1))
	sorted_dict2 = sorted(dict2.items(), key=operator.itemgetter(1))
	sorted_dict3 = sorted(dict3.items(), key=operator.itemgetter(1))
	sorted_dict4 = sorted(dict4.items(), key=operator.itemgetter(1))
	sorted_dict5 = sorted(dict5.items(), key=operator.itemgetter(1))

	total1=0
	total2=0
	total3=0
	total4=0
	total5=0

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
	




	# trace1 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[dict_top1[2][1]/total1, dict_top2[2][1]/total2, dict_top3[2][1]/total3, dict_top4[2][1]/total4, dict_top5[2][1]/total5], name='#1', text=[dict_top1[2][0], dict_top2[2][0], dict_top2[2][0], dict_top2[2][0], dict_top2[2][0]])

	# trace2 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[dict_top1[1][1]/total1, dict_top2[1][1]/total2, dict_top3[1][1]/total3, dict_top4[1][1]/total4, dict_top5[1][1]/total5], name='#2', text=[dict_top1[1][0], dict_top2[1][0], dict_top3[1][0], dict_top4[1][0], dict_top5[1][0]])
	# trace3 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[dict_top1[0][1]/total1, dict_top2[0][1]/total2, dict_top3[0][1]/total3, dict_top4[0][1]/total4, dict_top5[0][1]/total5], name='#3', text=[dict_top1[0][0], dict_top2[0][0], dict_top3[0][0], dict_top4[0][0], dict_top5[0][0]])


	# data = [trace1, trace2]
	# layout = go.Layout(barmode='group')
	# fig = go.Figure(data=data, layout=layout)
	# py.plot(fig, filename='grouped-bar-top-evolution')



	trace12 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[sorted_dict1[len(sorted_dict1)-1][1]/total1, sorted_dict2[len(sorted_dict2)-1][1]/total2, sorted_dict3[len(sorted_dict3)-1][1]/total3, sorted_dict4[len(sorted_dict4)-1][1]/total4, sorted_dict5[len(sorted_dict5)-1][1]/total5], name='#1', text=[sorted_dict1[len(sorted_dict1)-1][0], sorted_dict2[len(sorted_dict2)-1][0], sorted_dict3[len(sorted_dict3)-1][0], sorted_dict4[len(sorted_dict4)-1][0], sorted_dict5[len(sorted_dict5)-1][0]])

	trace22 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[sorted_dict1[len(sorted_dict1)-2][1]/total1, sorted_dict2[len(sorted_dict2)-2][1]/total2, sorted_dict3[len(sorted_dict3)-2][1]/total3, sorted_dict4[len(sorted_dict4)-2][1]/total4, sorted_dict5[len(sorted_dict5)-2][1]/total5], name='#2',text=[sorted_dict1[len(sorted_dict1)-2][0], sorted_dict2[len(sorted_dict2)-2][0], sorted_dict3[len(sorted_dict3)-2][0], sorted_dict4[len(sorted_dict4)-2][0], sorted_dict5[len(sorted_dict5)-2][0]])

	trace32 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=[sorted_dict1[len(sorted_dict1)-3][1]/total1, sorted_dict2[len(sorted_dict2)-3][1]/total2, sorted_dict3[len(sorted_dict3)-3][1]/total3, sorted_dict4[len(sorted_dict4)-3][1]/total4, sorted_dict5[len(sorted_dict5)-3][1]/total5], name='#3', text=[sorted_dict1[len(sorted_dict1)-3][0], sorted_dict2[len(sorted_dict2)-3][0], sorted_dict3[len(sorted_dict3)-3][0], sorted_dict4[len(sorted_dict4)-3][0], sorted_dict5[len(sorted_dict5)-3][0]])

	data1 = [trace12, trace22, trace32]
	layout1 = go.Layout(barmode='group')
	fig1 = go.Figure(data=data1, layout=layout1)
	py.plot(fig1, filename='grouped-bar-before')













#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------
#HELPER FUNCTIONS
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------

#======================================================================================================
#=========COMPUTES THE ABSOLUTE TOP 3 OF MOST EDITED AMENITIES AMONG NODES, WAYS AND RELATIONS=========
#======================================================================================================

def get_amenities_top():

	top =  [{'stop': 3282, 'bus_stop': 40200, 'no': 40200, 's': 8978, 'w': 7314}, {'prefeitura': 0, 'taxi_school': 0, 'kibanda cha mkaa': 0, 'highway': 40200, 'name': 40200}], [{'prefeitura': 0, 'taxi_school': 0, 'kibanda cha mkaa': 0, 'inss': 0, 'mausoleum': 0}, {'prefeitura': 0, 'taxi_school': 0, 'kibanda cha mkaa': 0, 'inss': 0, 'mausoleum': 0}]
	forbiddenEntries = {"yes", "no", "FIXME", "2", "s", "w", "name"}
	dict_top = {}


	for i in top:
		for elements in i: 
			for items in elements:
				if items not in dict_top and items not in forbiddenEntries:
					dict_top[items] = elements[items]


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

	#Dates computations
	event_date_convert = datetime.strptime(event_date,'%Y%m%d')
	date_before_convert = datetime.strptime(date_before,'%Y%m%d')

	#The number of weeks between event date and the date before the event
	diff_expected_user = (event_date_convert - date_before_convert).days /7

	#Average number of edits per user per week for the six months before
  	#This query is location proof
	expected_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d')+"'"+ where_clause + " GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d') + "' GROUP BY user_name) UNION ALL (SELECT count(*) as contributions, user_name from relations where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d') + "' GROUP BY user_name)) SELECT (SUM(contributions)/"+str(diff_expected_user)+") as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions)"])

	# a[0]: nb contrib/semaine
	# a[1]: user

	# Divides the expected user in 5 groups
	groups = [[],[],[],[],[]]

	expected_per_user.sort(key= lambda x : int (x[0]))
	
	i=0
	while (i<(len(expected_per_user) * 0.2)):
		groups[0].append(expected_per_user[i][1])
		i+=1
	while ((len(expected_per_user) * 0.2)<=i and i < (len(expected_per_user) * 0.4)):
		groups[1].append(expected_per_user[i][1])
		i+=1
	while( (len(expected_per_user) * 0.4 )<=i and i< (len(expected_per_user) * 0.6)):
		groups[2].append(expected_per_user[i][1])
		i+=1
	while ((len(expected_per_user) * 0.6)<=i and i<(len(expected_per_user) * 0.8)):
		groups[3].append(expected_per_user[i][1])
		i+=1
	while((len(expected_per_user) * 0.8)<=i and i<(len(expected_per_user))):
		groups[4].append(expected_per_user[i][1])
		i+=1

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
		if not abs(num - mean) <= factor * std_dev:
			data.remove(num)
			false_positive.append(num)

	print("Disregarded Data Points: ")
			
	return data

	















