import sys
import decimal
from datetime import datetime
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
plotly.tools.set_credentials_file(username='RomainDumon', api_key='4W9SerJqoMLaCR8e1abJ')

sys.path.insert(0, '../lib/')
# from db import DB

#==================================================================================
#=========All dates should have the format 'YearMonthDate' i.e. '20090311'=========
#==================================================================================
def abnormal_return_for_group(db, date_before, event_date , date_after, x = None, y = None):

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

	# Divides the expected user in 5 groups
	expected = {}
	groups = [[],[],[],[],[]]

	for a in expected_per_user:
		if a[0] > 0.0 and a[0] < 0.4:
			groups[0].append(a[1])
		if a[0] > 0.4 and a[0] < 4.0:
			groups[1].append(a[1])
		if a[0] > 4.0 and a[0] < 40.0:
			groups[2].append(a[1])
		if a[0] > 40.0 and a[0] < 400.0:
			groups[3].append(a[1])
		if a[0] > 400.0 and a[0] < 4000.0:
			groups[4].append(a[1])
		expected[a[1]] = a[0]
		print(str(a[0]) + "'"+str(a[1])+"'" )


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

	data = [group_1,group_2,group_3,group_4,group_5]
	py.plot(data,filename='box-plots osm London 3 month')

#-------------------------------------------------------------------------------
#Looking at evolution of deletes/creation and edits per day for a certain period
#-------------------------------------------------------------------------------
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


#-------------------------------------------------------------------------------
#-----------Impact of an import on creation to maintenance ratio----------------
#-----------Date before is included and event_date is not included--------------
#-------------------------------------------------------------------------------
def impact_import_creationtomaintenance_ratio(db, date_before, event_date, Graph_title):

	#Dates computations
	event_date_convert = datetime.strptime(event_date,'%Y%m%d')
	date_before_convert = datetime.strptime(date_before,'%Y%m%d')

	#The number of weeks between event date and the date before the event
	diff_expected_user = (event_date_convert - date_before_convert).days /7

	#Average number of edits per user per week for the six months before
  	#This query is location proof
	expected_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d')+"' GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d') + "' GROUP BY user_name) UNION ALL (SELECT count(*) as contributions, user_name from relations where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d') + "' GROUP BY user_name)) SELECT (SUM(contributions)/"+str(diff_expected_user)+") as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions)"])


	#Divides the expected user in 5 groups	
	groups = [[],[],[],[],[]] 

	for a in expected_per_user:
		if a[0] > 0.0 and a[0] < 0.4:
			groups[0].append(a[1])
		if a[0] > 0.4 and a[0] < 4.0:
			groups[1].append(a[1])
		if a[0] > 4.0 and a[0] < 40.0:
			groups[2].append(a[1])
		if a[0] > 40.0 and a[0] < 400.0:
			groups[3].append(a[1])
		if a[0] > 400.0 and a[0] < 4000.0:
			groups[4].append(a[1])

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


