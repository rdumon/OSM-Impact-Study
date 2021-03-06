import sys
import json
import decimal
import datetime
from dateutil.relativedelta import relativedelta
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import operator
import numpy as np
plotly.tools.set_credentials_file(username='aoussbai', api_key='jWkPjojJV8vrsSDbeU8J')
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
    expected_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d')+"'"+ where_clause + " GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d') + "' GROUP BY user_name)) SELECT (SUM(contributions)/"+str(diff_expected_user)+") as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions)"])

    expected = {}

    for a in expected_per_user:
        expected[a[1]] = a[0]

    #query average contribution for each user in each group
    actual_one_month = {}
    actual_per_user_one_month = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at > '" + event_date.strftime('%Y-%m-%d') + "' AND created_at < '" + date_after.strftime('%Y-%m-%d') +"'"+ where_clause + " GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at > '" + event_date.strftime('%Y-%m-%d') + "' AND created_at < '" + date_after.strftime('%Y-%m-%d') + "' GROUP BY user_name)) SELECT (SUM(contributions)/"+str(diff_actual_user)+") as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions)"])
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
        title = "Abnormal Return " +str(diff_actual_user) + " Weeks After Event",
        width=1200, height=540,
        yaxis = dict(range = [minVal,maxVal]),
    )

    data = [group_1,group_2,group_3,group_4,group_5]
    fig = dict(data = data, layout = layout)

    # py.plot(data,filename='box-plots osm London month')
    filelocation = dir_write_to['local']+'/abnormalReturnContrib'+str(diff_actual_user)+'weekAfter-'+date_after.strftime('%Y-%m-%d')+'.png'
    setPlotlyCredentials()
    retry = True
    while retry:
        try:
            retry = False
            py.image.save_as(fig,filename = filelocation)
        except (Exception, plotly.exceptions.PlotlyRequestError) as error:
            print('Plotly limit error... Don\'t care!')
            retry = True
            setPlotlyCredentials()

    # UPLOAD TO GOOGLE DRIVE
    filename = 'abnormalReturnContrib-'+str(diff_actual_user)+'weekAfter.png'
    googleDriveConnection.upload_GoogleDrive(filename,filelocation, dir_write_to['google'])

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
    delete_per_day = db.execute(["with C as((SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM nodes WHERE  created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after.strftime('%Y-%m-%d')+"'"+ " AND deleted = true GROUP BY created_at) UNION ALL (SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM ways WHERE  created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after.strftime('%Y-%m-%d')+"'"+ " AND deleted = true GROUP BY created_at)) SELECT created_at,SUM(contrib_deletion) as sum_contrib_deletion FROM C GROUP BY created_at ORDER BY created_at" ])

    # TODO
    delete_per_day_x = []
    delete_per_day_y = []
    for a in delete_per_day:
        delete_per_day_x.append((datetime.datetime.strptime(a[0],'%Y%m%d')).strftime('%Y-%m-%d'))
        delete_per_day_y.append(a[1])


    #work out evolution of creation contributions
    creation_per_day = db.execute(["with C as((SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM nodes WHERE  created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after.strftime('%Y-%m-%d')+"'"+ " AND version = 1 GROUP BY created_at) UNION ALL (SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM ways WHERE  created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after.strftime('%Y-%m-%d')+"'"+ " AND version = 1 GROUP BY created_at)) SELECT created_at,SUM(contrib_deletion) as sum_contrib_deletion FROM C GROUP BY created_at ORDER BY created_at" ])

    creation_per_day_x = []
    creation_per_day_y = []
    for a in creation_per_day:
        creation_per_day_x.append((datetime.datetime.strptime(a[0],'%Y%m%d')).strftime('%Y-%m-%d'))
        creation_per_day_y.append(a[1])

    # #work out evolution of edits contributions
    edits_per_day = db.execute(["with C as((SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM nodes WHERE  created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after.strftime('%Y-%m-%d')+"'"+ " AND deleted = false AND version != 1 GROUP BY created_at) UNION ALL (SELECT to_char(created_at,\'YYYYMMDD\') as created_at,count(*) as contrib_deletion FROM ways WHERE  created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at <= '" + date_after.strftime('%Y-%m-%d')+"'"+ " AND deleted = false AND version != 1 GROUP BY created_at)) SELECT created_at,SUM(contrib_deletion) as sum_contrib_deletion FROM C GROUP BY created_at ORDER BY created_at" ])

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
    setPlotlyCredentials()
    retry = True
    while retry:
        try:
            retry = False
            py.image.save_as(fig,filename = filelocation)
        except (Exception, plotly.exceptions.PlotlyRequestError) as error:
            print('Plotly limit error... Don\'t care!')
            retry = True
            setPlotlyCredentials()

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

    contribs_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d')+"' GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d') + "' GROUP BY user_name)) SELECT SUM(contributions) as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions)"])

    for a in contribs_per_user:
        dict_user_total_contribs[a[1]] = a[0]


    creates_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d')+"' AND version = 1 GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at >= '" + date_before_convert.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date_convert.strftime('%Y-%m-%d') + "' AND version = 1 GROUP BY user_name)) SELECT SUM(contributions) as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions)"])

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
    setPlotlyCredentials()
    retry = True
    while retry:
        try:
            retry = False
            py.plot(fig, filename='Maintenance vs Creations ' + Graph_title)
        except (Exception, plotly.exceptions.PlotlyRequestError) as error:
            print('Plotly limit error... Don\'t care!')
            retry = True
            setPlotlyCredentials()


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

    contribs_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d')+" 00:00:00' GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d') + " 00:00:00' GROUP BY user_name)) SELECT SUM(contributions) as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions) "])

    for a in contribs_per_user:
        dict_user_total_contribs[a[1]] = a[0]


    creates_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d')+" 00:00:00' AND version = 1 GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d') + " 00:00:00' AND version = 1 GROUP BY user_name)) SELECT SUM(contributions) as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions) "])

    for a in creates_per_user:
        dict_user_creates[a[1]] = a[0]

    #calculate expected ratio for each user over period given as input
    dict_user_expected_ratio = {}
    for k, v in dict_user_total_contribs.items():
        dict_user_expected_ratio[k] = dict_user_creates.get(k,decimal.Decimal(0.0)) / dict_user_total_contribs[k] / diff_expected_user

    #actual ratio per user for the period given as input
    contribs_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at <= '" + date_after.strftime('%Y-%m-%d') + "' AND created_at > '" + event_date.strftime('%Y-%m-%d')+" 24:00:00' GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at <= '" + date_after.strftime('%Y-%m-%d') + "' AND created_at > '" + event_date.strftime('%Y-%m-%d') + " 24:00:00' GROUP BY user_name)) SELECT SUM(contributions) as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions) "])

    for a in contribs_per_user:
        dict_user_total_contribs[a[1]] = a[0]


    creates_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at <= '" + date_after.strftime('%Y-%m-%d') + "' AND created_at > '" + event_date.strftime('%Y-%m-%d')+" 24:00:00' GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at <= '" + date_after.strftime('%Y-%m-%d') + "' AND created_at > '" + event_date.strftime('%Y-%m-%d') + " 24:00:00' GROUP BY user_name)) SELECT SUM(contributions) as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions) "])

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
            if user in dict_user_actual_ratio and user in dict_user_expected_ratio:
                abnormal_return_per_group[group_num].append(dict_user_actual_ratio[user]-dict_user_expected_ratio[user])
        group_num += 1

    group_1 = go.Box(
        # y=trim_95Perc_rule(abnormal_return_per_group[0]),
        y=abnormal_return_per_group[0],
        name = 'Group 1',
        boxpoints = False,
    )
    group_2 = go.Box(
        y=abnormal_return_per_group[1],
        # y=trim_95Perc_rule(abnormal_return_per_group[1]),
        name = 'Group 2',
        boxpoints = False,
    )
    group_3 = go.Box(
        # y=trim_95Perc_rule(abnormal_return_per_group[2]),
        y=abnormal_return_per_group[2],
        name = 'Group 3',
        boxpoints = False,
    )
    group_4 = go.Box(
        # y=trim_95Perc_rule(abnormal_return_per_group[3]),
        y=abnormal_return_per_group[3],
        name = 'Group 4',
        boxpoints = False,
    )
    group_5 = go.Box(
        # y=trim_95Perc_rule(abnormal_return_per_group[4]),
        y=abnormal_return_per_group[4],
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
    setPlotlyCredentials()
    retry = True
    while retry:
        try:
            retry = False
            py.image.save_as(fig,filename = filelocation)
        except (Exception, plotly.exceptions.PlotlyRequestError) as error:
            print('Plotly limit error... Don\'t care!')
            retry = True
            setPlotlyCredentials()

    # UPLOAD TO GOOGLE DRIVE
    filename = 'abnormalReturnMaintenance'+str(diff_actual_user)+'.png'
    googleDriveConnection.upload_GoogleDrive(filename,filelocation, dir_write_to['google'])

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
def top_amenity_evolution_per_group(groups, db,googleDriveConnection, date_before,event_date,date_after, x=None, y=None, import_dir =''):

    print(event_date,date_after,date_before)

    #Dates computations

    where_clause = ' '
    if x!=None and y!=None and len(x) == 2 and len(y) == 2:
        where_clause += 'AND latitude > '+str(x[1])+' AND longitude > '+str(x[0])+' AND latitude < '+str(y[1])+' AND longitude < '+str(y[0])

    amenity_type_per_user_before_nodes= " SELECT json_agg(tags) as tags, user_name FROM nodes WHERE created_at >= '" + date_before.strftime('%Y-%m-%d') +"' AND created_at < '" + (event_date+relativedelta(days=-1)).strftime('%Y-%m-%d')+" 00:00:00'"+ where_clause + " GROUP BY user_name"

    amenity_type_per_user_after_nodes = " SELECT json_agg(tags) as tags, user_name FROM nodes WHERE created_at < '" + date_after.strftime('%Y-%m-%d') +"' AND created_at > '" + (event_date+relativedelta(days=+1)).strftime('%Y-%m-%d')+" 00:00:00'"+ where_clause + " GROUP BY user_name"

    amenity_type_per_user_before_ways= " SELECT json_agg(tags) as tags, user_name FROM ways WHERE created_at >= '" + date_before.strftime('%Y-%m-%d') +"' AND created_at < '" + (event_date+relativedelta(days=-1)).strftime('%Y-%m-%d')+" 00:00:00' GROUP BY user_name"

    amenity_type_per_user_after_ways = " SELECT json_agg(tags) as tags, user_name FROM ways WHERE created_at < '" + date_after.strftime('%Y-%m-%d') +"' AND created_at > '" + (event_date+relativedelta(days=+1)).strftime('%Y-%m-%d')+" 00:00:00' GROUP BY user_name"

    amenity_type_per_user_before_all = "SELECT json_agg(result.tags) as tags, result.user_name FROM (" + amenity_type_per_user_before_nodes + " UNION ALL " + amenity_type_per_user_before_ways+") AS result GROUP BY result.user_name"

    amenity_type_per_user_after_all = "SELECT json_agg(result.tags) as tags, result.user_name FROM (" + amenity_type_per_user_after_nodes + " UNION ALL " + amenity_type_per_user_after_ways+") AS result GROUP BY result.user_name"

    analysis_before = db.execute([amenity_type_per_user_before_all])
    analysis_after = db.execute([amenity_type_per_user_after_all])
    analyses = [analysis_before, analysis_after]


    refDict = build_dictionary_of_amenities()
    forbiddenEntries = {"yes", "no", "FIXME", "2", "s", "w", "name", "1", "4", "unclassified", "-1"}

    dict_total = [{}, {}, {}, {}, {}]

    dict_total2 = [{}, {}, {}, {}, {}]


    for fields in analysis_before:
        for count in range(0,5):
            if fields[1] in groups[count]:
                for tag in fields[0]:
                        for data in tag:
                            for detail in data:
                                if data[detail] in refDict and data[detail] not in forbiddenEntries:
                                    if data[detail] in dict_total[count]:
                                        dict_total[count][data[detail]]+=1
                                    else:
                                        dict_total[count][data[detail]] =1
                                elif detail in refDict and detail not in forbiddenEntries:
                                    if detail in dict_total[count]:
                                        dict_total[count][detail]+=1
                                    else:
                                        dict_total[count][detail] =1

    for fields in analysis_after:
        for count in range(0,5):
            if fields[1] in groups[count]:
                for tag in fields[0]:
                        for data in tag:
                            for detail in data:
                                if data[detail] in refDict and data[detail] not in forbiddenEntries:
                                    if data[detail] in dict_total2[count]:
                                        dict_total2[count][data[detail]]+=1
                                    else:
                                        dict_total2[count][data[detail]] =1
                                elif detail in refDict and detail not in forbiddenEntries:
                                    if detail in dict_total2[count]:
                                        dict_total2[count][detail]+=1
                                    else:
                                        dict_total2[count][detail] =1

    sorted_dict_total = [{}, {}, {}, {}, {}]

    for i in range (0,5):
        sorted_dict_total[i] = sorted(dict_total[i].items(), key=operator.itemgetter(1), reverse=True)

    sorted_dict_total2 = [{}, {}, {}, {}, {}]

    for i in range (0,5):
        sorted_dict_total2[i] = sorted(dict_total2[i].items(), key=operator.itemgetter(1), reverse=True)

    total_agg1 = [0,0,0,0,0]

    total_agg2 = [0,0,0,0,0]

    for i in range (0,5):
        for j in range (0, len(sorted_dict_total[i])-1):
            total_agg1[i]+=sorted_dict_total[i][j][1]

    for i in range (0,5):
        for j in range (0, len(sorted_dict_total2[i])-1):
            total_agg2[i]+=sorted_dict_total2[i][j][1]

    ordonnes = [[], [], []]
    text = [[], [], []]

    for j in range (0,3):
        for i in range (0,5):
            if total_agg1[i] == 0:
                ordonnes[j].append(0)
            else:
                ordonnes[j].append(sorted_dict_total[i][j][1]/float(total_agg1[i]))

    for j in range (0,3):
        for i in range (0,len(sorted_dict_total)):
            text[j].append(sorted_dict_total[i][j][0])

    trace_before1 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=ordonnes[0], name='#1', text=text[0])
    trace_before2 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=ordonnes[1], name='#2', text=text[1])
    trace_before3 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=ordonnes[2], name='#3', text=text[2])

    data1 = [trace_before1, trace_before2, trace_before3]
    layout1 = go.Layout(barmode='group', title='Top 3 Most Edited Ammenity Type Before Import',width=1200, height=540,)
    fig1 = go.Figure(data=data1, layout=layout1)

    ordonness = [[], [], []]

    textt = [[], [], []]

    for j in range (0,3):
        for i in range (0,5):
            try:
                if total_agg2[i] == 0:
                    ordonness[j].append(0)
                else:
                    ordonness[j].append(sorted_dict_total2[i][j][1]/float(total_agg2[i]))
            except(IndexError) as error:
                ordonness[j].append("name not provided")

    for j in range (0,3):
        for i in range (0,5):
            try:
                if len(sorted_dict_total2[i]) == 0:
                    textt[j].append("")
                else:
                    textt[j].append(sorted_dict_total2[i][j][0])
            except(IndexError) as error:
                textt[j].append("Undefined")


    trace_after1 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=ordonness[0], name='#1', text=textt[0])
    trace_after2 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=ordonness[1], name='#2', text=textt[1])
    trace_after3 = go.Bar( x=['group 1', 'group 2', 'group 3', 'group 4', 'group 5'], y=ordonness[2], name='#3', text=textt[2])

    data12 = [trace_after1, trace_after2, trace_after3]
    layout12 = go.Layout(barmode='group', title= 'Top 3 Most Edited Ammenity Type After Import',width=1200, height=540,)
    fig12 = go.Figure(data=data12, layout=layout12)

    # # SAVE LOCALLY
    setPlotlyCredentials()
    retry = True
    while retry:
        try:
            retry = False
            py.image.save_as(fig1, filename=import_dir['local']+'/top_amenity_focus_before'+event_date.strftime('%Y-%m-%d')+'.png')
        except (Exception, plotly.exceptions.PlotlyRequestError) as error:
            print('Plotly limit error... Don\'t care!')
            retry = True
            setPlotlyCredentials()

    # # UPLOAD TO GOOGLE DRIVE
    filename = 'top_amenity_focus_before'+event_date.strftime('%Y-%m-%d')+'.png'
    filelocation = import_dir['local']+'/top_amenity_focus_before'+event_date.strftime('%Y-%m-%d')+'.png'
    googleDriveConnection.upload_GoogleDrive(filename,filelocation, import_dir['google'])


    # # SAVE LOCALLY
    setPlotlyCredentials()
    retry = True
    while retry:
        try:
            retry = False
            py.image.save_as(fig12, filename=import_dir['local']+'/top_amenity_focus_after'+event_date.strftime('%Y-%m-%d')+'.png')
        except (Exception, plotly.exceptions.PlotlyRequestError) as error:
            print('Plotly limit error... Don\'t care!')
            retry = True
            setPlotlyCredentials()

    # # UPLOAD TO GOOGLE DRIVE
    filename = 'top_amenity_focus_after'+event_date.strftime('%Y-%m-%d')+'.png'
    filelocation = import_dir['local']+'/top_amenity_focus_after'+event_date.strftime('%Y-%m-%d')+'.png'
    googleDriveConnection.upload_GoogleDrive(filename,filelocation, import_dir['google'])



def top_import_amenity_abnormal_return(groups, db,googleDriveConnection, date_before,event_date,date_after, iMport, x=None, y=None, import_dir =''):

    #Dates computations

    # Queries
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

    analyses = [analysis_before,analysis_after]


    refDict = build_dictionary_of_amenities()
    forbiddenEntries = {"yes", "no", "FIXME", "2", "s", "w", "name", "1", "4", "unclassified", "-1",""}
    absol_dict = get_amenities_top(db, iMport)

    top1 = list(absol_dict)[0]

    # Before variable
    user_ratio_group_total = [{}, {}, {}, {}, {}]   # Contrib of each user for the ammenity of the import
    user_contrib_group_total = [{}, {}, {}, {}, {}] # All contribs

    # After variable
    user_ratio_group_total2 = [{}, {}, {}, {}, {}]   # Contrib of each user for the ammenity of the import
    user_contrib_group_total2 = [{}, {}, {}, {}, {}] # All contribs


    #=====================here we count the number of contributions per user for the top amenity and the total contributions====================================

    # We fill the variables
    for fields in analysis_before:
        user = fields[1]
        for count in range(0,5):
            if user in groups[count]:
                for tag in fields[0]:
                        for data in tag:
                            for detail in data:
                                if data[detail] == top1 or detail== top1:
                                    if user in user_ratio_group_total[count]:
                                        user_ratio_group_total[count][user]+=1
                                    else:
                                        user_ratio_group_total[count][user] = 1


                                if (data[detail] in refDict and data[detail] not in forbiddenEntries) or (detail in refDict and detail not in forbiddenEntries):
                                    if user in user_contrib_group_total[count]:
                                        user_contrib_group_total[count][user]+=1
                                    else:
                                        user_contrib_group_total[count][user] =1

    # Same for after
    for fields in analysis_after:
        for count in range(0,5):
            if fields[1] in groups[count]:
                for tag in fields[0]:
                        for data in tag:
                            for detail in data:
                                if data[detail] == top1 or detail == top1:
                                    if fields[1] in user_ratio_group_total2[count]:
                                        user_ratio_group_total2[count][fields[1]]+=1
                                    else:
                                        user_ratio_group_total2[count][fields[1]] =1


                                if (data[detail] in refDict and data[detail] not in forbiddenEntries) or (detail in refDict and detail not in forbiddenEntries):
                                    if fields[1] in user_contrib_group_total2[count]:
                                        user_contrib_group_total2[count][fields[1]]+=1
                                    else:
                                        user_contrib_group_total2[count][fields[1]] =1

    #============================now we can calculate the ratio per user for each group============================================

    ratio_total = [{}, {}, {}, {}, {}]

    ratio_total2 = [{}, {}, {}, {}, {}]

    # Calculate ratio before
    for dictio in  user_contrib_group_total:
        for user in dictio:
            for i in range(0,5):
                if user in groups[i]:
                    if dictio[user]==0:
                        ratio_total[i][user]=0
                    else:
                        if len(user_ratio_group_total[i])!=0 and user in user_ratio_group_total[i]:
                            ratio_total[i][user] = user_ratio_group_total[i][user] / float(dictio[user])

    #  Calculate ratio after
    for dictio in  user_contrib_group_total2:
        for user in dictio:
            for i in range(0,5):
                if user in groups[i]:
                    if dictio[user]==0:
                        ratio_total2[i][user]=0
                    else:
                        if len(user_ratio_group_total2[i])!=0 and len(dictio)!=0 and user in user_ratio_group_total2[i]:
                            ratio_total2[i][user] = user_ratio_group_total2[i][user] / float(dictio[user])

    # =============== Now we calculate abnormal return =============

    dataAbnormal = []

    for i in range(0,len(ratio_total)):
        data = []
        counter=0
        for user in ratio_total[i]:
            data.append(ratio_total2[i].get(user,(0.0)) - ratio_total[i].get(user,(0.0)))

        dataAbnormal.append(data)

    #=========================now we plot the box plots================================================

    group_1 = go.Box(
            y=dataAbnormal[0],
            # y=trim_95Perc_rule(dataAbnormal[0]),
            name = 'Group 1',
            boxpoints = False,
        )
    group_2 = go.Box(
            y=dataAbnormal[1],
            # y=trim_95Perc_rule(dataAbnormal[1]),
            name = 'Group 2',
            boxpoints = False,
        )
    group_3 = go.Box(
            y=dataAbnormal[2],
            # y=trim_95Perc_rule(dataAbnormal[2]),
            name = 'Group 3',
            boxpoints = False,
        )
    group_4 = go.Box(
            y=dataAbnormal[3],
            # y=trim_95Perc_rule(dataAbnormal[3]),
            name = 'Group 4',
            boxpoints = False,
        )
    group_5 = go.Box(
            y=dataAbnormal[4],
            # y=trim_95Perc_rule(dataAbnormal[4]),
            name = 'Group 5',
            boxpoints = False,
        )

    layout = go.Layout(
            title = "Abnormal Return of Ratio Import Main Amenity Type to Total contributions" ,
            width=1200, height=540,
        )

    data = [group_1,group_2,group_3,group_4,group_5]
    fig = dict(data = data, layout = layout)

    # # SAVE LOCALLY
    setPlotlyCredentials()
    retry = True
    while retry:
        try:
            retry = False
            py.image.save_as(fig, filename=import_dir['local']+'/import_amenity_focus_before'+event_date.strftime('%Y-%m-%d')+'.png')
        except (Exception, plotly.exceptions.PlotlyRequestError) as error:
            print('Plotly limit error... Don\'t care!')
            retry = True
            setPlotlyCredentials()

    # # UPLOAD TO GOOGLE DRIVE
    filename = 'import_amenity_focus_before'+event_date.strftime('%Y-%m-%d')+'.png'
    filelocation = import_dir['local']+'/import_amenity_focus_before'+event_date.strftime('%Y-%m-%d')+'.png'
    googleDriveConnection.upload_GoogleDrive(filename,filelocation, import_dir['google'])

    # ==== SET UP FOR JSON
    filename = "import_amenity_focus_before-"+event_date.strftime('%Y-%m-%d')+".json"
    filelocation = import_dir['local']+"/"+filename

    # == CHANGE DECIMAL OBJECTS TO FLOAT DATA POINTS
    for data in dataAbnormal:
        for i in range(0,len(data)):
            data[i] = float(data[i])
    json_info = { "data " : dataAbnormal}

    #====MAKE JSON======
    with open(filelocation, "w") as f:
        json.dump(json_info, f)

    # UPLOAD TO GOOGLE DRIVE
    googleDriveConnection.upload_GoogleDrive(filename,filelocation, import_dir['google'], 'text/json')


#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------
#HELPER FUNCTIONS
#-----------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------

#===================================================================================================================
#=========DETECTS THE ABSOLUTE TOP 1 OF MOST EDITED AMENITIES AMONG NODES, WAYS AND RELATIONS OF AN IMPORT=========
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

    absol_dict = dict(sorted(dict_top.items(), key=operator.itemgetter(1), reverse=True)[:1])

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

    group_contrib = [0,0,0,0,0]

    for a in expected_per_user:
        if a[0] > 0.0 and a[0] < 10.0:
            groups[0].append(a[1])
            group_contrib[0] += a[0]
        if a[0] > 10.0 and a[0] < 100.0:
            groups[1].append(a[1])
            group_contrib[1] += a[0]
        if a[0] > 100.0 and a[0] < 1000.0:
            groups[2].append(a[1])
            group_contrib[2] += a[0]
        if a[0] > 1000.0 and a[0] < 10000.0:
            groups[3].append(a[1])
            group_contrib[3] += a[0]
        if a[0] > 10000.0:
            groups[4].append(a[1])
            group_contrib[4] += a[0]

    # Print groups count
    totalContrib = 0
    for index in range(0,5):
        totalContrib+=group_contrib[index]

    for index in range(0,5):
        print("Users in  Group "+str(index)+": "+str( len(groups[index]) ))
        print("Contrib ratio of Group "+str(index)+": "+str( group_contrib[index]/totalContrib ))
    return groups

def group_analyserv2(db, date_before, event_date):

    #The number of weeks between event date and the date before the event

    #Average number of edits per user per week for the six months before
      #This query is location proof
    expected_per_user = db.execute(["with C as((SELECT count(*) as contributions, user_name from nodes where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d')+"'  GROUP BY user_name)UNION ALL (SELECT count(*) as contributions, user_name from ways where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d') + "' GROUP BY user_name) UNION ALL (SELECT count(*) as contributions, user_name from relations where created_at >= '" + date_before.strftime('%Y-%m-%d') + "' AND created_at < '" + event_date.strftime('%Y-%m-%d') + "' GROUP BY user_name)) SELECT SUM(contributions) as contributions, user_name from C GROUP BY user_name ORDER BY SUM(contributions)"])

    # a[0]: nb contrib/semaine
    # a[1]: user

    # Build dictionnary of birthdate
    creation_date_query = "SELECT user_name, min(created_at) from (select user_name,to_char(min(created_at),'YYYYMMDD') as created_at from nodes  group by user_name UNION ALL select user_name, to_char(min(created_at),'YYYYMMDD') as created_at from ways group by user_name) as A group by user_name"
    temp_all_birthday = db.execute([creation_date_query]);
    all_birthday = {}
    for item in temp_all_birthday:
        all_birthday[item[0]] = item[1]

    # ======= Remove "virgin" user =======
    #  Only applicable after 2007 as it's the creation date of OSM
    if date_before > datetime.datetime.strptime('2008-01-01', '%Y-%m-%d'):
        print("Checking for new users to remove...")
        for user in expected_per_user:
            if user[1] in all_birthday and date_before < datetime.datetime.strptime(all_birthday[user[1]], '%Y%m%d'):
                # print(user[1]+ ': ' +str(all_birthday[user[1]]) +" is a virgin ... "+ str(date_before.strftime('%Y-%m-%d')) )
                expected_per_user.remove(user)
    # Divides the expected user in 5 groups
    groups = [[],[],[],[],[]]

    total_contributions = 0
    total_user = 0
    for a in expected_per_user:
        total_contributions += a[0]
        total_user +=1

    threshold = []
    diff = total_contributions /5

    # ======== BY percentage =============
    threshold.append(total_contributions)                       #5
    threshold.append(decimal.Decimal(0.99)*total_contributions) #10
    threshold.append(decimal.Decimal(0.97)*total_contributions) #15
    threshold.append(decimal.Decimal(0.90)*total_contributions) #20
    threshold.append(decimal.Decimal(0.60)*total_contributions) #50

    expected_per_user.sort(key= lambda x : int (x[0]))

    current_sum = 0
    user_counter = len(expected_per_user)-1

    for index in range(0,5):
        groups[4-index].append(expected_per_user[user_counter][1])
        current_sum += expected_per_user[user_counter][0]
        user_counter-=1
        while current_sum < threshold[4-index]:
            groups[4-index].append(expected_per_user[user_counter][1])
            current_sum += expected_per_user[user_counter][0]
            user_counter-=1

    # Print groups count
    for index in range(0,5):
        print("Group "+str(index)+": "+str(len(groups[index])))

    return groups

#================================================================================================
#=========Trips a list and returns a list with the bottom 2% remove and upper 2% removed=========
#================================================================================================
def trim_95Perc_rule(data):

    size_of_list = len(data)

    if size_of_list == 1:
        return data

    std_dev = np.std(data)
    mean = np.mean(data)

    factor = 2
    false_positive = []
    for num in data:
        if not abs(num - mean) <= (factor * std_dev):
            data.remove(num)
            false_positive.append(num)

    return data

# ===============================================================================================
# ============================SURVIVAL ANALYSIS==================================================
# ===============================================================================================

def survivalAnalysis(db,googleDriveConnection, groups, date_before, event_date, import_dir):
    timeOfDeath = db.execute(["select MAX(max) as date, user_name from ((select user_name, max(created_at) from nodes group by user_name order by user_name) union all (select user_name, max(created_at) from ways group by user_name order by user_name) union all (select user_name, max(created_at) from relations group by user_name order by user_name)) as t group by user_name;"])
    # select date, count(user_name) from () as x group by date

    users = []
    time = []

    timeOfDeath.sort()

    for (x,y) in timeOfDeath:
        time.append(x)
        users.append(y)

    resultByGroups = [[[]],[[]],[[]],[[]],[[]]]
    counter = 0
    finalTimes = [[],[],[],[],[]]
    finalIndex = 0
    finalCounts = []
    index = [0,0,0,0,0]
    previousDateIndex = [0,0,0,0,0]
    group = 0
    groupAssigned = False
    isFirst = [True, True, True, True, True]
    time.sort()

    for i in timeOfDeath:
        if time[counter].date() >= date_before.date():
            if users[counter] in groups[0]:
                group = 0
                groupAssigned = True
            if users[counter] in groups[1]:
                group = 1
                groupAssigned = True
            if users[counter] in groups[2]:
                group = 2
                groupAssigned = True
            if users[counter] in groups[3]:
                group = 3
                groupAssigned = True
            if users[counter] in groups[4]:
                group = 4
                groupAssigned = True

            if groupAssigned == True:
                if isFirst[group] == True:
                    previousDateIndex[group] = counter
                    isFirst[group] = False

                if time[previousDateIndex[group]].date() != time[counter].date():
                    finalTimes[group].append(time[previousDateIndex[group]].date())
                    index[group] += 1
                    resultByGroups[group].append([])
                previousDateIndex[group] = counter
                resultByGroups[group][index[group]].append(users[counter])
        groupAssigned = False
        counter += 1

    totalUsers = []

    totalDeathsByDay = [[],[],[],[],[]]

    for i in range(0,5):
        for array in resultByGroups[i]:
            totalDeathsByDay[i].append(len(array))

    for i in range(0,5):
        totalUsers.append(len(groups[i]))



    activeUsers = [[],[],[],[],[]]

    for i in range(0,5):
        for j in totalDeathsByDay[i]:
            activeUsers[i].append(totalUsers[i])
            totalUsers[i] -= j



    trace1 = go.Scatter(
    x = finalTimes[0],
    y = activeUsers[0],
    name= "Group 0"
    )
    trace2 = go.Scatter(
    x = finalTimes[1],
    y = activeUsers[1],
    name= "Group 1"
    )
    trace3 = go.Scatter(
    x = finalTimes[2],
    y = activeUsers[2],
    name= "Group 2"
    )
    trace4 = go.Scatter(
    x = finalTimes[3],
    y = activeUsers[3],
    name= "Group 3"
    )
    trace5 = go.Scatter(
    x = finalTimes[4],
    y = activeUsers[4],
    name= "Group 4"
    )
    layout = {
        'shapes': [
            # Line Vertical
            {
                'type': 'line',
                'x0': event_date,
                'y0': 0,
                'x1': event_date,
                'y1': len(groups[0]),
                'line': {
                    'color': 'rgb(55, 128, 191)',
                    'width': 3,
                },
            }
        ]
    }

    data = [ trace1 ,trace2, trace3, trace4, trace5]
    fig = {
        'data': data,
        'layout': layout,
    }

    # # SAVE LOCALLY
    setPlotlyCredentials()
    retry = True
    while retry:
        try:
            retry = False
            py.image.save_as(fig, filename=import_dir['local']+'/survival analysis'+event_date.strftime('%Y-%m-%d')+'.png')
        except (Exception, plotly.exceptions.PlotlyRequestError) as error:
            print(error)
            print('Plotly limit error... Don\'t care!')
            retry = True
            setPlotlyCredentials()

    # # UPLOAD TO GOOGLE DRIVE
    filename = 'survival analysis'+event_date.strftime('%Y-%m-%d')+'.png'
    filelocation = import_dir['local']+'/survival analysis'+event_date.strftime('%Y-%m-%d')+'.png'
    googleDriveConnection.upload_GoogleDrive(filename,filelocation, import_dir['google'])

#================================================================================================
#================================RANGE FINDER====================================================
#================================================================================================
def find_range(data):

    return [np.min(data),np.max(data)]


# =============== Avoid plotly limitation ===============
plotCred = [
    ['RomainDumon','cJVtOQ4pZHAaQcBeTULV'],
    ['aoussbai','uWPqQZwnbe5MgCrfqk3V'],
    ['JhumanJ','xUuKkx6qmi5j3E75OpgT'],
    ['charlydes','6ufsK3cLlAp4DUzohtm8'],
    ['kristelle', 'SurOvd0IiMprlmA3k7rp'],
    ['llimitover','VQ8YvSNNskEMFjVDm4XN'],
    ['overlimit','lAKTXvobkgW7oUYEH1Zn'],
    ['wallahlalimite','1s4kglYj7dDu6QhMJoWX'],
    ['sorryplotlyineedyou','iOUg5UCjPQdUfjYBWkVv']
]
currentPlotlyAccount = 0

def setPlotlyCredentials():
    global currentPlotlyAccount, plotCred

    print("Using: "+str(plotCred[currentPlotlyAccount]))
    plotly.tools.set_credentials_file(username=plotCred[currentPlotlyAccount][0], api_key=plotCred[currentPlotlyAccount][1])
    currentPlotlyAccount += 1

    if(len(plotCred) == currentPlotlyAccount):
        currentPlotlyAccount = 0
