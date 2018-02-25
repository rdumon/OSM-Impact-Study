import sys
import decimal
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
plotly.tools.set_credentials_file(username='RomainDumon', api_key='4W9SerJqoMLaCR8e1abJ')

sys.path.insert(0, '../lib/')
from db import DB

def abnormal_return_for_group(db, event_date, month_before, month_after):
	#Average number of edits per user per week for the six months before
  	#This query is location proof
	expected_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at >= '2008-10-01' AND created_at < '2009-04-01' AND latitude > 2414900 AND longitude > 514749580 AND latitude < -25770000 AND longitude < 515409360 GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at >= '2008-10-01' AND created_at < '2009-04-01' GROUP BY user_name) UNION ALL (SELECT count(*) as contributions, user_name from relations where created_at >= '2008-10-01' AND created_at < '2009-04-01' GROUP BY user_name)) SELECT (SUM(contributions)/26) as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions)"])

	# build a dictionary with those results
	expected = {}

	#list of all user in each group
	group1 = []
	group2 = []
	group3 = []
	group4 = []
	group5 = []
		
	for a in expected_per_user:
		if a[0] > 0.0 and a[0] < 0.4:
			group1.append(a[1])
		if a[0] > 0.4 and a[0] < 4.0:
			group2.append(a[1])
		if a[0] > 4.0 and a[0] < 40.0:
			group3.append(a[1])
		if a[0] > 40.0 and a[0] < 400.0:
			group4.append(a[1])
		if a[0] > 400.0 and a[0] < 4000.0:
			group5.append(a[1])
		expected[a[1]] = a[0]

	groups = []
	groups.append(group1)
	groups.append(group2)
	groups.append(group3)
	groups.append(group4)
	groups.append(group5)


	#query average contribution for each user in each group
	actual_one_month = {}
	actual_per_user_one_month = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at >= '2009-04-01' AND created_at < '2009-05-01' AND latitude > 2414900 AND longitude > 514749580 AND latitude < -25770000 AND longitude < 515409360 GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at >= '2009-04-01' AND created_at < '2009-05-01' GROUP BY user_name) UNION ALL (SELECT count(*) as contributions, user_name from relations where created_at >= '2009-04-01' AND created_at < '2009-05-01' GROUP BY user_name)) SELECT (SUM(contributions)/4) as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions)"])
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
	py.plot(data)

       




