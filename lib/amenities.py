import sys
import json

with open('/home/romaindumon/Documents/UCL/Year3/Research/OSM-Impact-Study/lib/amenities.json') as data_file:    
    data = json.load(data_file)


#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------
#SET OF VARIABLES AND FUNCTIONS USEFUL TO LOOK AT AMENITIES
#----------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------


def build_dictionary_of_amenities():

	dictionary_amenities = {} 

	for object in data["data"]:
		dictionary_amenities[object["value"]] = 0

	return dictionary_amenities




