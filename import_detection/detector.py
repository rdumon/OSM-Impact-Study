"""
This module does all the analysis to detect an import

def detectImport(db,cityName='', x = None , y = None, dir_write_to = '', googleDriveConnection = '', detectionLevel = ):
def find_contribution_type_of_import(db, iMport = [], table =""):
def imports_report(db, googleDriveConnection, imports= [], dir_write_to = ''):

"""

import sys
import json
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import operator

from operator import itemgetter
import datetime
from lib.amenities import *


def detectImport(db,cityName='', x = None , y = None, dir_write_to = '', googleDriveConnection = '', detectionLevel = 20):
    """
    DB is the database
    X is the lower left point
    Y is the upper right point
    """

    # Queries
    creation_date_query = "SELECT user_name, min(created_at) from (select user_name,to_char(min(created_at),'YYYYMMDD') as created_at from nodes  group by user_name UNION ALL select user_name, to_char(min(created_at),'YYYYMMDD') as created_at from ways group by user_name) as A group by user_name"

    all_contribution_node_query = 'select to_char(created_at,\'YYYYMMDD\') as created_at, user_name, count(*) as contrib from nodes group by user_name, to_char(created_at,\'YYYYMMDD\')'
    all_contribution_way_query = 'select to_char(created_at,\'YYYYMMDD\') as created_at, user_name, count(*) as contrib from ways group by user_name, to_char(created_at,\'YYYYMMDD\')'

    all_contribution_query = 'SELECT created_at, user_name, SUM(A.contrib) as contrib FROM ( '+ all_contribution_node_query+' UNION ALL '+ all_contribution_way_query+') as A group by user_name,created_at ;'

    # Get dictionnary of birthdate of each user
    temp_all_birthday = db.execute([creation_date_query]);
    all_birthday = {}
    for item in temp_all_birthday:
        all_birthday[item[0]] = item[1]

    # Get daily contribution of each user
    all_contribution = db.execute([all_contribution_query]);
    all_contribution = sorted(all_contribution, key=itemgetter(0))

    # Graph of best user
    daily_best_contrib = {'value':[], 'date':[], 'user':[]}
    daily_max = all_contribution[0][2]
    daily_date = all_contribution[0][0]
    daily_user = all_contribution[0][1]
    for day_contrib in all_contribution:
        if day_contrib[0]==daily_date:
            if day_contrib[2] > daily_max:
                daily_max = day_contrib[2]
                daily_user = day_contrib[1]
        else:
            daily_best_contrib['value'].append(daily_max)
            daily_best_contrib['date'].append(datetime.datetime.strptime(daily_date, "%Y%m%d"))
            daily_best_contrib['user'].append(daily_user)
            daily_max = day_contrib[2]
            daily_user = day_contrib[1]
            daily_date = day_contrib[0]

    # Construct array of first contrib foe each user and their value
    data = []
    for day_contrib in all_contribution:
        if all_birthday[day_contrib[1]] == day_contrib[0]:
            data.append(day_contrib)

    # Sort data
    data = sorted(data, key=itemgetter(0))

    # Now we only keep the best for each day
    # ------- Graphs of best new user contribution --------
    current_date = data[0][0]
    current_max = data[0][2]
    current_max_user = data[0][1]

    daily_best_new_user_contrib = {'value':[], 'date':[], 'user':[]}


    graph_date = []
    graph_val = []
    graph_text = []
    for item in data:
        if item[0] == current_date:
            if item[2] > current_max:
                current_max = item[2]
                current_max_user = item[1]
        else:
            daily_best_new_user_contrib['date'].append(datetime.datetime.strptime(current_date, "%Y%m%d"))
            daily_best_new_user_contrib['value'].append(current_max)
            daily_best_new_user_contrib['user'].append(current_max_user)

            current_date = item[0]
            current_max = item[2]
            current_max_user = item[1]

    average_new_user = sum(daily_best_new_user_contrib['value']) / len(daily_best_new_user_contrib['value'])
    average = sum(daily_best_contrib['value']) / len(daily_best_contrib['value'])
    import_limit = average * detectionLevel

    # Now we plot all graphs
    trace0 = go.Scatter(
        x = daily_best_new_user_contrib['date'],
        y = daily_best_new_user_contrib['value'],
        text = daily_best_new_user_contrib['user'],
        name = "Daily best new user contribution"
    )

    trace1 = go.Scatter(
        x = daily_best_new_user_contrib['date'],
        y = [average_new_user] * len(daily_best_new_user_contrib['date']),
        name = "Average daily best new user contribution"
    )

    trace2 = go.Scatter(
        x = daily_best_contrib['date'],
        y = daily_best_contrib['value'],
        text = daily_best_contrib['user'],
        name = "Daily best contribution"
    )

    trace3 = go.Scatter(
        x = daily_best_contrib['date'],
        y = [average] * len(daily_best_contrib['value']),
        name = "Average daily best user contribution"
    )

    trace4 = go.Scatter(
        x = daily_best_contrib['date'],
        y = [import_limit] * len(daily_best_contrib['value']),
        name = "Import Limit"
    )

    data_graph = [trace2,trace3,trace0,trace1,trace4]

    # py.plot(data_graph, filename=('Import Detection '+cityName))

    layout = go.Layout(title = "Import Detection "+cityName,width=1200, height=540)

    data = [trace2,trace3,trace0,trace1,trace4]
    fig = dict(data = data, layout = layout)
    # py.plot(data,filename='box-plots osm London month')
    filelocation = dir_write_to['local']+'/import-dectection.png'

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
    filename = 'import-dectection.png'
    googleDriveConnection.upload_GoogleDrive(filename,filelocation, dir_write_to['google'])

    detected_imports = []
    for i in range(0,len(daily_best_contrib['value'])):
        if daily_best_contrib['value'][i] >= import_limit:
            detected_imports.append([daily_best_contrib['date'][i],daily_best_contrib['user'][i]])

    return (detected_imports,import_limit)

def find_contribution_type_of_import(db, iMport = [], table =""):

    user_name = iMport[1]
    date_convert = iMport[0]

    query = "SELECT json_agg(tags) as tags, id FROM "+table+" WHERE created_at > '" + date_convert.strftime('%Y-%m-%d') + " 00:00:00' AND created_at < '" + date_convert.strftime('%Y-%m-%d') + " 24:00:00' AND user_name = '"+user_name+"' GROUP BY id  "

    #do not need to worry about version number (we assume that import is only creation or one time edits to change twice a node) List of tuples
    amenity_type_of_all_nodes_of_import = db.execute([query])

    dict_amenities_right_fields = build_dictionary_of_amenities()
    dict_amenities_left_fields = build_dictionary_of_amenities()

    unidentified = 0

    for tuple in amenity_type_of_all_nodes_of_import:
        for json in tuple[0]:
            for item in json:
                try:
                    dict_amenities_right_fields[json[item].lower()] += 1
                except KeyError:
                    unidentified += 1
                    continue

    for tuple in amenity_type_of_all_nodes_of_import:
        for json in tuple[0]:
            for item in json:
                try:
                    dict_amenities_left_fields[item.lower()] += 1
                except KeyError:
                    unidentified += 1
                    continue

    list_top = []
    list_top.append(dict(sorted(list(dict_amenities_right_fields.items()), key=operator.itemgetter(1), reverse=True)[:5]))
    list_top.append(dict(sorted(list(dict_amenities_left_fields.items()), key=operator.itemgetter(1), reverse=True)[:5]))

    return list_top

def imports_report(db, googleDriveConnection, imports= [], dir_write_to = '',import_limit=0):

    imports_information = []
    array = []
    for iMport in imports:
        array.append(iMport)

        array.append(find_contribution_type_of_import(db, iMport, "nodes"))
        # print("Analysing its ways: ".upper())
        array.append(find_contribution_type_of_import(db, iMport, "ways"))
        imports_information.append(array)
        array = []

    # Create a JSON out of this data and Push it to Drive
    # ==== SET UP FOR JSON
    filename = "importsInfo.json"
    filelocation = dir_write_to['local']+"/"+filename

    # Change to JSON format
    json_info = {}
    import_counter = 0
    for iMport in imports_information:
        import_counter += 1
        json_info['import'+str(import_counter)] = []
        for array in iMport:
            for element in array:
                if isinstance(element, datetime.datetime):
                    json_info['import'+str(import_counter)].append(element.strftime("%Y-%m-%d"))
                else:
                    json_info['import'+str(import_counter)].append(element)
    json_info['import_limit'] = int(import_limit)

    #====MAKE JSON======
    with open(filelocation, "w") as f:
        json.dump(json_info, f)

    # UPLOAD TO GOOGLE DRIVE
    googleDriveConnection.upload_GoogleDrive(filename,filelocation, dir_write_to['google'], 'text/json')


    return imports_information

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
