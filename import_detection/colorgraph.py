import sys
import plotly
import plotly.plotly as py
from plotly.graph_objs import *
import random
plotly.tools.set_credentials_file(username='RomainDumon', api_key='EfFe07aVY131PpodoWqG')
mapbox_access_token = 'pk.eyJ1Ijoib3NtcHJvamVjdDMwOTYiLCJhIjoiY2plb2ZpcTByMDFiYjMycXkwajE4d2Q2MiJ9.DhyGCvF6LCEgnjfgrWLVQg'

sys.path.insert(0, '../lib/')
from lib.db import DB


#Import info is the array expecting the [[datetime.datetime(2009, 8, 17, 0, 0), 'NaPTAN']] and the name of the city
def draw_heatMap(db, importInfo = [], x=None, y=None):

	where_clause = ''
	# if x!=None and y!=None and len(x) == 2 and len(y) == 2:
		# where_clause = '(latitude > '+str(x[1])+' and longitude > '+str(x[0])+') and (latitude < '+str(y[1])+' and longitude < '+str(y[0])+')'

	middle_lat = (x[0] + (abs(y[0]-x[0])/2.0))/10000000.0
	middle_long = (x[1] + (abs(y[1]-x[1])/2.0))/10000000.0

	user_name = importInfo[0][1] 
	date_convert = importInfo[0][0]

	query = "SELECT latitude, longitude  FROM nodes WHERE created_at > '" + date_convert.strftime('%Y-%m-%d') + " 00:00:00' AND created_at < '" + date_convert.strftime('%Y-%m-%d') + " 24:00:00' AND user_name = '"+user_name+"'  "+where_clause+" GROUP BY latitude, longitude"


	nodes = db.execute([query])

	lats = []
	longs = []

	for point in nodes:
		longs.append(point[0]/10000000.0)
		lats.append(point[1]/10000000.0)


	data = Data([
	    Scattermapbox(
	        lat=lats,
	        lon=longs,
	        mode='markers',
	        marker=Marker(
	            size=5,
	            color='rgb('+str(random.randint(100, 255))+','+str(random.randint(100, 255))+','+str(random.randint(100, 255))+')',
	        )
	        
	    )
	])
	layout = Layout(
	    autosize=True,
	    hovermode='closest',
	    mapbox=dict(
	        accesstoken=mapbox_access_token,
	        bearing=0,
	        center=dict(
	            lat=middle_lat,
	            lon=middle_long
	        ),
	        pitch=0,
	        zoom=10
	    ),
	)

	fig = dict(data=data, layout=layout)
	py.plot(fig, filename='Multiple Mapbox')