import sys
import psycopg2
import decimal
from impact_analyzer import *

sys.path.insert(0, '../lib/')
from db import DB

import plotly
import plotly.plotly as py
import plotly.graph_objs as go
plotly.tools.set_credentials_file(username='RomainDumon', api_key='4W9SerJqoMLaCR8e1abJ')

NODE_TYPE="Nodes"
WAY_TYPE="Ways"
RELATION_TYPE="Relations"

config = {
    'DB_NAME':'osmlondon',
    'DB_USER':'romaindumon',
    'DB_PWD':'',
    'DB_HOST':'',
    'DB_PORT':'5432'
}


if __name__ == '__main__':

	db = DB(config)
	







		






