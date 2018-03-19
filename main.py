import sys
import json
from import_detection.detector import *
from impact.impact_analyzer import *


from lib.db import DB
from import_detection.detector import detectImport

# ======== Open Config =======
with open('config.json') as json_file:
    config = json.load(json_file)

# ======== Create Database =======
db = DB(config['DB'])

# Detect import
# x = [501355000,298938000]
# y = [506677000,311696000]
x = [513694000,-4465000]  #en bas a gauche
y = [516374000,1921000] #en haut a droite
print(detectImport(db,'London',x,y))
# detectWaysImport(db,'London',x,y)

# abnormal_return_for_group(db,'20110401','20111001','20120501',x,y)
