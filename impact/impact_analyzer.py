import sys
import decimal
from datetime import datetime
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
plotly.tools.set_credentials_file(username='RomainDumon', api_key='4W9SerJqoMLaCR8e1abJ')

sys.path.insert(0, '../lib/')
from db import DB

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

	#Divides the expected user in 5 groups	
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
			print(user + ' '+str(abnormalReturnPerUser_one_month[user]))
		dataAbnormal.append(data)
		print('Next Group')



	trace0 = go.Box(
    	y=dataAbnormal[0]
	)
	trace1 = go.Box(
    	y=dataAbnormal[1]
	)
	trace2 = go.Box(
    	y=dataAbnormal[2]
	)
	trace3 = go.Box(
    	y=dataAbnormal[3]
	)
	trace4 = go.Box(
    	y=dataAbnormal[4]
	)

	data = [trace0,trace1,trace2,trace3,trace4]
	py.plot(data,filename='box-plots osm London')

       




