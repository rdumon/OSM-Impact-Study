import sys
import psycopg2
import decimal
from impact_analyzer import *

sys.path.insert(0, '../lib/')
from db import DB

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
	x = [513694000,-4465000]
	y = [516374000,1921000]
	abnormal_return_for_group(db,'20111101','20120429','20121101',x,y)









		






