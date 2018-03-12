import sys
import json
import plotly.plotly as py
import plotly.graph_objs as go
import operator

from operator import itemgetter
import datetime
from lib.amenities import *



# ========== Code ================

# DB is the database
# X is the lower left point
# Y is the upper right point

def detectImport(db,cityName='',x=None,y=None):

    # If there is a location restriction
    where_clause = ''
    if x!=None and y!=None and len(x) == 2 and len(y) == 2:
        where_clause = 'where (latitude > '+str(x[1])+' and longitude > '+str(x[0])+') and (latitude < '+str(y[1])+' and longitude < '+str(y[0])+')'

    # Queries
    creation_date_query = 'select user_name, to_char(min(created_at),\'YYYYMMDD\') as created_at from nodes '+where_clause+' group by user_name'
    all_contribution_query = 'select to_char(created_at,\'YYYYMMDD\') as created_at, user_name, count(*) as contrib from nodes '+where_clause+' group by user_name, to_char(created_at,\'YYYYMMDD\')'

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
    import_limit = average * 20

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

    data_graph = [trace0, trace1,trace2,trace3,trace4]

    # py.plot(data_graph, filename=('Import Detection '+cityName))

    detected_imports = []
    for i in range(0,len(daily_best_contrib['value'])):
        print(str(daily_best_contrib['value'][i]) + ' vs '+ str(import_limit))
        if daily_best_contrib['value'][i] >= import_limit:
            detected_imports.append([daily_best_contrib['date'][i],daily_best_contrib['user'][i]])

    return detected_imports

def detectWaysImport(db,cityName='',x=None,y=None):

    # If there is a location restriction
    where_clause = ''
    ways_where_clause = ''
    if x!=None and y!=None and len(x) == 2 and len(y) == 2:
        where_clause = 'where (latitude > '+str(x[1])+' and longitude > '+str(x[0])+') and (latitude < '+str(y[1])+' and longitude < '+str(y[0])+')'
        ways_where_clause = ' and count(case when (latitude > '+str(x[1])+' and longitude > '+str(x[0])+') and (latitude < '+str(y[1])+' and longitude < '+str(y[0])+') then 0 end) > 0 '

    # Queries
    ways_query = 'select count(ways.id), user_name from ways_nodes JOIN ways ON ways.id = ways_nodes.id AND ways.version = ways_nodes.version'
    ways_query += ' group by user_name having ( count(*)>1' + ways_where_clause +' )'

    # TODO: add group by date

    print(ways_query)
    sys.exit(-1)

    creation_date_query = 'select user_name, to_char(min(created_at),\'YYYYMMDD\') as created_at from nodes '+where_clause+' group by user_name'
    all_contribution_query = 'select to_char(created_at,\'YYYYMMDD\') as created_at, user_name, count(*) as contrib from nodes '+where_clause+' group by user_name, to_char(created_at,\'YYYYMMDD\')'

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

    # Now we plot all graphs
    trace0 = go.Scatter(
        x = daily_best_new_user_contrib['date'],
        y = daily_best_new_user_contrib['value'],
        text = daily_best_new_user_contrib['user'],
        name = "Daily best new user contribution"
    )

    trace1 = go.Scatter(
        x = daily_best_new_user_contrib['date'],
        y = [sum(daily_best_new_user_contrib['value']) / len(daily_best_new_user_contrib['value'])] * len(daily_best_new_user_contrib['date']),
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
        y = [sum(daily_best_contrib['value']) / len(daily_best_contrib['value'])] * len(daily_best_contrib['value']),
        name = "Average daily best user contribution"
    )

    data_graph = [trace0, trace1,trace2,trace3]

    py.plot(data_graph, filename=('Import Ways Detection '+cityName))



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
    list_top.append(dict(sorted(dict_amenities_right_fields.iteritems(), key=operator.itemgetter(1), reverse=True)[:5]))
    list_top.append(dict(sorted(dict_amenities_left_fields.iteritems(), key=operator.itemgetter(1), reverse=True)[:5]))

    print("Top 5 for the left fields of the tags:")
    print(dict(sorted(dict_amenities_right_fields.iteritems(), key=operator.itemgetter(1), reverse=True)[:3]))
    print("Top 5 for the right fields of the tags:")
    print(dict(sorted(dict_amenities_left_fields.iteritems(), key=operator.itemgetter(1), reverse=True)[:3]))
    print("Unidentified fields were ignored : " + str(unidentified))

    return list_top

def imports_report(db, imports= []):

    imports_information = []
    array = []
    for iMport in imports:
        array.append(iMport)
        print("#################################################################################################")
        print("The import happened in "+ iMport[0].strftime('%Y-%m-%d') + " and was done by user : "+ iMport[1])
        print("Analysing its nodes: ".upper())
        array.append(find_contribution_type_of_import(db, iMport, "nodes"))
        print("Analysing its ways: ".upper())
        array.append(find_contribution_type_of_import(db, iMport, "ways"))
        imports_information.append(array)
        array = []
    return imports_information
    









